import React from 'react';
import { cn } from "@/lib/utils";

interface TerminalCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  status?: 'idle' | 'active' | 'danger' | 'success';
}

export function TerminalCard({ title, children, className, status = 'idle' }: TerminalCardProps) {
  // Dynamic border colors based on status
  const borderColor = 
    status === 'danger' ? 'border-[#ff0055]' : 
    status === 'success' ? 'border-[#00ff9d]' : 
    'border-[#27272a]';

  const headerColor = 
    status === 'danger' ? 'text-[#ff0055] bg-[#ff0055]/10' : 
    status === 'success' ? 'text-[#00ff9d] bg-[#00ff9d]/10' : 
    'text-[#a1a1aa] bg-[#09090b]';

  return (
    <div className={cn("relative bg-black border-2 flex flex-col", borderColor, className)}>
      {/* Decorative corner brackets */}
      <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-current opacity-50" />
      <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-current opacity-50" />

      {/* Header */}
      <div className={cn("px-3 sm:px-4 py-2 text-xs font-bold uppercase tracking-widest border-b border-[#27272a] flex justify-between items-center", headerColor)}>
        <span className="truncate">/// {title}</span>
        <div className="flex gap-1">
           {/* Status Lights */}
           <span className={`w-1.5 h-1.5 ${status === 'active' ? 'bg-[#00ff9d] animate-pulse' : 'bg-[#27272a]'}`} />
           <span className={`w-1.5 h-1.5 ${status === 'danger' ? 'bg-[#ff0055] animate-pulse' : 'bg-[#27272a]'}`} />
        </div>
      </div>

      {/* Content Area */}
      <div className="p-4 sm:p-6 relative flex-1 min-h-0 overflow-hidden">
         {children}
      </div>
    </div>
  );
}

