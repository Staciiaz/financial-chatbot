import LoginForm from "./LoginForm";

export default function LoginPage() {
  const registrationEnabled = process.env.ENABLE_REGISTRATION !== "false";
  return <LoginForm registrationEnabled={registrationEnabled} />;
}
