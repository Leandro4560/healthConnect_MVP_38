import { config } from 'dotenv';

config();

const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: Number(process.env.DB_PORT) || 5432,
  username: process.env.DB_USER || 'user',
  password: process.env.DB_PASS || 'password',
  database: process.env.DB_NAME || 'mydatabase',
};

const serverConfig = {
  port: Number(process.env.PORT) || 3000,
};

export { dbConfig, serverConfig };