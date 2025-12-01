import request from "supertest";
import mongoose from "mongoose";
import { MongoMemoryServer } from "mongodb-memory-server";
import app from "../../backend/app.js";
import User from "../../backend/models/User.js";

let mongoServer;

beforeAll(async () => {
  // ensure JWT secret exists for createToken/signing
  process.env.JWT_SECRET = process.env.JWT_SECRET || "test_jwt_secret";
  // ensure cookies are not set with secure flag in tests
  process.env.NODE_ENV = "development";
  // request a MongoDB binary version compatible with recent Debian images
  // (mongodb-memory-server fails for older MongoDB binaries on Debian 12+)
  // when running inside docker-compose test-runner we prefer using the real
  // mongo service instead of downloading in-container mongod binaries
  if (process.env.MONGO_URI) {
    await mongoose.connect(process.env.MONGO_URI);
  } else {
    // default behavior for local dev: let mongodb-memory-server pick the
    // version it prefers (previously worked locally, avoids large downloads)
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri);
  }
});

afterAll(async () => {
  await mongoose.disconnect();
  if (mongoServer && typeof mongoServer.stop === "function") {
    await mongoServer.stop();
  }
});

beforeEach(async () => {
  await User.deleteMany({});
});

test("POST /api/v1/users - register user", async () => {
  const res = await request(app)
    .post("/api/v1/users")
    .send({ username: "test", email: "test@example.com", password: "123456" })
    .expect(201);

  expect(res.body).toMatchObject({ username: "test", email: "test@example.com" });
  expect(res.headers["set-cookie"]).toBeDefined();
});

test("POST /api/v1/users/auth - login user", async () => {
  await request(app)
    .post("/api/v1/users")
    .send({ username: "test", email: "test@example.com", password: "123456" });

  const res = await request(app)
    .post("/api/v1/users/auth")
    .send({ email: "test@example.com", password: "123456" })
    .expect(201);

  expect(res.body).toMatchObject({ email: "test@example.com", username: "test" });
  expect(res.headers["set-cookie"]).toBeDefined();
});

test("GET /api/v1/users/profile - protected route", async () => {
  const agent = request.agent(app);
  await agent
    .post("/api/v1/users")
    .send({ username: "test", email: "test@example.com", password: "123456" })
    .expect(201);

  const res = await agent.get("/api/v1/users/profile").expect(200);

  expect(res.body).toMatchObject({ username: "test", email: "test@example.com" });
});

test("POST /api/v1/users/logout - logs out", async () => {
  const agent = request.agent(app);

  await agent
    .post("/api/v1/users")
    .send({ username: "test", email: "test@example.com", password: "123456" })
    .expect(201);

  const res = await agent.post("/api/v1/users/logout").expect(200);
  expect(res.body).toMatchObject({ message: "Logged out successfully" });
});
