// Packages
import express from "express";
import cookieParser from "cookie-parser";
import dotenv from "dotenv";
import path from "path";

// Files
import connectDB from "./config/db.js";
import app from "./app.js";

// Configuration
dotenv.config();
connectDB();

const PORT = process.env.PORT || 3000;

// connect to DB then start
connectDB();

app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));
