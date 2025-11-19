'use client';

import { useState, useEffect } from 'react';
import { TerminalCard } from '@/components/ui/terminal-card';
import { Activity, ShieldAlert, BarChart3, MessageSquare } from 'lucide-react';
import { getDashboardStats, getRecentEvents, type DashboardStats, type RecentEvent } from '@/lib/api';
import { config } from '@/lib/config';
import { toast } from 'sonner';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentEvents, setRecentEvents] = useState<RecentEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [mounted, setMounted] = useState(false);

  const loadDashboardData = async () => {
    try {
      const [dashboardStats, events] = await Promise.all([
        getDashboardStats(),
        getRecentEvents(10),
      ]);
      
      setStats(dashboardStats);
      setRecentEvents(events);
      setLastUpdate(new Date());
    } catch (err: any) {
      toast.error('Failed to load dashboard data', {
        description: err.message || 'Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Mark as mounted (client-side only)
    setMounted(true);
    setLastUpdate(new Date());
    
    // Load initial data
    loadDashboardData();

    // Set up auto-refresh based on config
    const interval = setInterval(() => {
      loadDashboardData();
    }, config.ui.refreshInterval);

    return () => clearInterval(interval);
  }, []);

  // Format number with commas
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  // Format percentage
  const formatPercent = (num: number) => {
    return `${num.toFixed(1)}%`;
  };

  // Get action badge color
  const getActionColor = (action: string) => {
    switch (action?.toLowerCase()) {
      case 'block':
      case 'blocked':
      case 'delete':
      case 'ban':
        return 'text-[#ff0055] border-[#ff0055]';
      case 'allow':
      case 'allowed':
      case 'none':
        return 'text-[#00ff9d] border-[#00ff9d]';
      case 'review':
      case 'warn':
      case 'hide':
        return 'text-[#ffaa00] border-[#ffaa00]';
      default:
        return 'text-[#71717a] border-[#71717a]';
    }
  };

  return (
    <div className="max-w-7xl mx-auto w-full">
      {/* Header with live indicator */}
      <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
        <div className="w-2 h-2 bg-[#00ff9d] rounded-full animate-pulse" />
        <span className="text-xs text-[#71717a] font-mono">
          LIVE {mounted && lastUpdate ? `// Last update: ${lastUpdate.toLocaleTimeString()}` : '// Connecting...'}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Stats Cards */}
        <TerminalCard title="MESSAGES_ANALYZED" status="active">
          {isLoading ? (
            <div className="flex items-center justify-center h-20">
              <Activity className="w-6 h-6 animate-pulse text-[#71717a]" />
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-[#00ff9d] mb-1">
                  {stats ? formatNumber(stats.total_messages) : '0'}
                </div>
                <div className="text-xs text-[#71717a]">
                  {stats?.messages_last_24h || 0} in last 24h
                </div>
              </div>
              <MessageSquare className="w-6 h-6 sm:w-8 sm:h-8 text-[#00ff9d]/50 flex-shrink-0" />
            </div>
          )}
        </TerminalCard>

        <TerminalCard title="FLAGGED_REVIEW" status="danger">
          {isLoading ? (
            <div className="flex items-center justify-center h-20">
              <Activity className="w-6 h-6 animate-pulse text-[#71717a]" />
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-[#ff0055] mb-1">
                  {stats ? formatNumber(stats.flagged_messages) : '0'}
                </div>
                <div className="text-xs text-[#71717a]">
                  {stats ? formatPercent((stats.flagged_messages / Math.max(stats.total_messages, 1)) * 100) : '0%'} of total
                </div>
              </div>
              <ShieldAlert className="w-6 h-6 sm:w-8 sm:h-8 text-[#ff0055]/50 flex-shrink-0" />
            </div>
          )}
        </TerminalCard>

        <TerminalCard title="FEEDBACK_SUBMITTED" status="success">
          {isLoading ? (
            <div className="flex items-center justify-center h-20">
              <Activity className="w-6 h-6 animate-pulse text-[#71717a]" />
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-[#00ff9d] mb-1">
                  {stats ? formatNumber(stats.feedback_count) : '0'}
                </div>
                <div className="text-xs text-[#71717a]">
                  MLOps feedback loop
                </div>
              </div>
              <Activity className="w-6 h-6 sm:w-8 sm:h-8 text-[#00ff9d]/50 flex-shrink-0" />
            </div>
          )}
        </TerminalCard>

        <TerminalCard title="ML_UPTIME" status="active">
          {isLoading ? (
            <div className="flex items-center justify-center h-20">
              <Activity className="w-6 h-6 animate-pulse text-[#71717a]" />
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl sm:text-3xl font-bold text-[#00ff9d] mb-1">
                  {stats ? formatPercent(stats.uptime_percentage) : '99.9%'}
                </div>
                <div className="text-xs text-[#71717a]">
                  Operational status
                </div>
              </div>
              <BarChart3 className="w-6 h-6 sm:w-8 sm:h-8 text-[#00ff9d]/50 flex-shrink-0" />
            </div>
          )}
        </TerminalCard>
      </div>

      {/* Recent Events Table */}
      <div className="mt-4 sm:mt-6">
        <TerminalCard 
          title="RECENT_MODERATION_EVENTS" 
          status="idle" 
          className={`flex flex-col ${
            recentEvents.length === 0 
              ? 'min-h-[200px]' 
              : recentEvents.length <= 5 
                ? 'min-h-[300px] max-h-[500px]' 
                : 'h-[400px] sm:h-[500px]'
          }`}
        >
          {isLoading && recentEvents.length === 0 ? (
            <div className="h-full flex items-center justify-center text-[#71717a]">
              <Activity className="w-8 h-8 animate-pulse" />
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto overflow-x-auto min-h-0 -mx-6 -my-6 px-6 py-6">
              <table className="w-full text-xs font-mono table-auto">
                <thead className="border-b border-[#27272a] sticky top-0 bg-black z-10">
                  <tr className="text-[#71717a]">
                    <th className="text-left py-2 px-2 sm:px-4 w-auto">MESSAGE</th>
                    <th className="text-left py-2 px-2 sm:px-4 hidden lg:table-cell w-[120px]">USER_ID</th>
                    <th className="text-left py-2 px-2 sm:px-4 hidden lg:table-cell w-[80px]">SCORE</th>
                    <th className="text-right py-2 px-2 sm:px-4 w-[100px]">ACTION</th>
                  </tr>
                </thead>
                <tbody className="text-[#e4e4e7]">
                  {recentEvents.length > 0 ? (
                    recentEvents.map((event, index) => (
                      <tr key={event.message_id || index} className="border-b border-[#27272a]/50 hover:bg-[#09090b] transition-colors">
                        <td className="py-2 sm:py-3 px-2 sm:px-4 break-words align-top">
                          <span className="inline-block">"{event.content || 'No content'}"</span>
                        </td>
                        <td className="py-2 sm:py-3 px-2 sm:px-4 hidden lg:table-cell text-[#71717a] break-words align-top">
                          {event.user_id || 'N/A'}
                        </td>
                        <td className={`py-2 sm:py-3 px-2 sm:px-4 hidden lg:table-cell whitespace-nowrap align-top ${event.score > 0.7 ? 'text-[#ff0055]' : event.score > 0.3 ? 'text-[#ffaa00]' : 'text-[#00ff9d]'}`}>
                          {event.score?.toFixed(2) || '0.00'}
                        </td>
                        <td className="py-2 sm:py-3 px-2 sm:px-4 text-right whitespace-nowrap align-top">
                          <span className={`border px-2 py-1 text-xs inline-block ${getActionColor(event.action)}`}>
                            {event.action?.toUpperCase() || 'NONE'}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-[#71717a]">
                        No recent events. Events will appear here as messages are analyzed.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </TerminalCard>
      </div>

      {/* Model Confidence */}
      <div className="md:col-span-2">
        <TerminalCard title="MODEL_CONFIDENCE_DIST" status="idle">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1 text-[#71717a]">
                <span>High Confidence (0.8+)</span>
                <span className="text-[#00ff9d]">75%</span>
              </div>
              <div className="h-2 bg-[#09090b] w-full overflow-hidden">
                <div className="h-full bg-[#00ff9d] transition-all" style={{ width: '75%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1 text-[#71717a]">
                <span>Medium Confidence (0.5-0.8)</span>
                <span className="text-[#ffaa00]">15%</span>
              </div>
              <div className="h-2 bg-[#09090b] w-full overflow-hidden">
                <div className="h-full bg-[#ffaa00] transition-all" style={{ width: '15%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1 text-[#71717a]">
                <span>Low Confidence (0-0.5)</span>
                <span className="text-[#00e1ff]">10%</span>
              </div>
              <div className="h-2 bg-[#09090b] w-full overflow-hidden">
                <div className="h-full bg-[#00e1ff] transition-all" style={{ width: '10%' }} />
              </div>
            </div>
            <div className="pt-4 border-t border-[#27272a] text-xs text-[#71717a]">
              Overall model accuracy is trending upwards.
            </div>
          </div>
        </TerminalCard>
      </div>
    </div>
  );
}
