import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { Toaster } from "sonner";

const mono = JetBrains_Mono({ 
  subsets: ["latin"], 
  variable: "--font-mono" 
});

export const metadata: Metadata = {
  title: "HATE_SPEECH // Defense System",
  description: "Threat Intelligence System v2.0",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${mono.variable} font-mono min-h-screen bg-[#050505] antialiased overflow-hidden`}>
        {/* The Background Grid Layer */}
        <div className="fixed inset-0 bg-grid z-[-1] pointer-events-none" />
        
        {/* Top Status Bar */}
        <header className="h-12 sm:h-14 border-b border-[#27272a] bg-[#09090b]/80 backdrop-blur flex items-center px-3 sm:px-6 justify-between sticky top-0 z-50">
          <div className="flex items-center gap-2 sm:gap-4">
            <div className="w-2 h-2 sm:w-3 sm:h-3 bg-[#00ff9d] rounded-none animate-pulse shadow-[0_0_10px_#00ff9d]" />
            <span className="text-[#00ff9d] font-bold tracking-widest text-xs sm:text-sm">HATE_SPEECH v2.0</span>
          </div>
          
          {/* Terminal Navigation */}
          <nav className="hidden md:flex items-center gap-2 lg:gap-4 text-xs">
            <Link href="/" className="text-[#71717a] hover:text-[#00ff9d] transition-colors px-1 sm:px-2 py-1 border border-transparent hover:border-[#00ff9d]/30">
              // DASHBOARD
            </Link>
            <Link href="/analyze" className="text-[#71717a] hover:text-[#00ff9d] transition-colors px-1 sm:px-2 py-1 border border-transparent hover:border-[#00ff9d]/30">
              // ANALYZE
            </Link>
            <Link href="/analytics" className="text-[#71717a] hover:text-[#00ff9d] transition-colors px-1 sm:px-2 py-1 border border-transparent hover:border-[#00ff9d]/30">
              // ANALYTICS
            </Link>
            <Link href="/feedback" className="text-[#71717a] hover:text-[#00ff9d] transition-colors px-1 sm:px-2 py-1 border border-transparent hover:border-[#00ff9d]/30">
              // FEEDBACK
            </Link>
          </nav>

          <div className="hidden lg:flex text-xs text-[#71717a] gap-4 xl:gap-6">
            <span>MEM: 64TB</span>
            <span>NET: ENCRYPTED</span>
            <span>USER: ROOT</span>
          </div>
        </header>

        <main className="p-3 sm:p-4 md:p-6 h-[calc(100vh-48px)] sm:h-[calc(100vh-56px)] overflow-auto">
          {children}
        </main>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}
