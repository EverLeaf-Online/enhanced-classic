const { z } = require("zod");

const MIN_LENGTH = 8;
const MAX_LENGTH = 12;
const REQUIREMENT = `Password must be ${MIN_LENGTH}-${MAX_LENGTH} characters to work in both the website and game client.`;

const compatiblePassword = z.string().min(MIN_LENGTH).max(MAX_LENGTH);
const loginPassword = z.string().min(1).max(100);

const registrationSchema = z.object({
  username: z.string().regex(/^[A-Za-z0-9_]{4,13}$/),
  password: compatiblePassword,
  confirmPassword: compatiblePassword,
  email: z.string().email().max(45),
  agree: z.literal("yes")
}).refine(value => value.password === value.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"]
});

const passwordChangeSchema = z.object({
  // Deliberately keep accepting existing passwords longer than the client limit.
  // Affected players must be able to sign in on the website and shorten them.
  currentPassword: loginPassword,
  newPassword: compatiblePassword,
  confirmPassword: compatiblePassword
}).refine(value => value.newPassword === value.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"]
});

module.exports = {
  MIN_LENGTH,
  MAX_LENGTH,
  REQUIREMENT,
  loginPassword,
  registrationSchema,
  passwordChangeSchema
};
