import RegisterForm from "./RegisterForm";

export default function RegisterPage() {
  const registrationEnabled = process.env.ENABLE_REGISTRATION !== "false";
  return <RegisterForm registrationEnabled={registrationEnabled} />;
}
