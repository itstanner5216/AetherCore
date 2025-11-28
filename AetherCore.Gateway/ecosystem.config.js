module.exports = {
  apps: [
    {
      name: "gateway",
      cwd: ".",
      script: "uvicorn",
      interpreter: "python",
      args: "gateway:app --host 0.0.0.0 --port 8000",
      env: {
        PYTHONUNBUFFERED: "1",
        PYTHONDONTWRITEBYTECODE: "1",
        PYTHONPATH: "/app/Aethercore.Gateway",
        LOG_LEVEL: "info",
      },
    },
    {
      name: "search-helper",
      cwd: ".",
      script: "server.js",
      interpreter: "node",
      env: {
        PORT: "3000",
        NODE_ENV: "production",
      },
    },
  ],
};
