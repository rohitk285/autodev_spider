const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch((error) => {
    // If a response has already been sent by the controller, forwards
    // the error to the next middleware to avoid "Cannot set headers"
    // and double-responses.
    if (res.headersSent) {
      return next(error);
    }

    // Respect any status code already set on the response (e.g. controller
    // may set res.status(400) then throw). Fall back to 500 otherwise.
    const status = res.statusCode && res.statusCode !== 200 ? res.statusCode : 500;
    res.status(status).json({ message: error.message });
  });
};

export default asyncHandler;
