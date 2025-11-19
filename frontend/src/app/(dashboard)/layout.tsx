export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Terminal UI - no sidebar/header needed (handled in root layout)
  return <>{children}</>;
}

