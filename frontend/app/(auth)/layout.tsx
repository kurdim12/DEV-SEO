/**
 * Auth layout - minimal layout for login and register pages.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="w-full max-w-md p-8">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-primary">DevSEO</h1>
          <p className="text-sm text-muted-foreground mt-2">
            AI-Powered SEO Analysis
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
