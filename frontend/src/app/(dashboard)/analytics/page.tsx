'use client';

import { useState, useEffect } from 'react';
import { TerminalCard } from '@/components/ui/terminal-card';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getAnalytics } from '@/lib/api';
import { toast } from 'sonner';
import { Activity } from 'lucide-react';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await getAnalytics();
      setAnalytics(data);
    } catch (err: any) {
      toast.error('Failed to load analytics', {
        description: err.message || 'Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Mock data for demonstration
  const timeSeriesData = [
    { date: '01-01', messages: 1200, flagged: 180 },
    { date: '01-02', messages: 1350, flagged: 195 },
    { date: '01-03', messages: 1500, flagged: 210 },
    { date: '01-04', messages: 1420, flagged: 200 },
    { date: '01-05', messages: 1680, flagged: 240 },
  ];

  const actionDistribution = [
    { name: 'ALLOWED', value: 75, color: '#00ff9d' },
    { name: 'BLOCKED', value: 15, color: '#ff0055' },
    { name: 'REVIEW', value: 10, color: '#ffaa00' },
  ];

  return (
    <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 w-full">
      {/* Time Series Chart */}
      <TerminalCard title="MESSAGE_VOLUME_TIMELINE" status="active" className="lg:col-span-2 h-[300px] sm:h-[350px] lg:h-[400px]">
        {isLoading ? (
          <div className="h-full flex items-center justify-center text-[#71717a]">
            <Activity className="w-8 h-8 animate-pulse" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="date" stroke="#71717a" style={{ fontSize: '12px' }} />
              <YAxis stroke="#71717a" style={{ fontSize: '12px' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#09090b', 
                  border: '1px solid #27272a',
                  color: '#e4e4e7',
                  borderRadius: '4px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="messages" 
                stroke="#00ff9d" 
                strokeWidth={2}
                dot={{ fill: '#050505', stroke: '#00ff9d', strokeWidth: 2, r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="flagged" 
                stroke="#ff0055" 
                strokeWidth={2}
                dot={{ fill: '#050505', stroke: '#ff0055', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </TerminalCard>

      {/* Action Distribution */}
      <TerminalCard title="ACTION_DISTRIBUTION" status="idle" className="h-[250px] sm:h-[300px]">
        {isLoading ? (
          <div className="h-full flex items-center justify-center text-[#71717a]">
            <Activity className="w-8 h-8 animate-pulse" />
          </div>
        ) : (
          <div className="space-y-4">
            {actionDistribution.map((item) => (
              <div key={item.name}>
                <div className="flex justify-between text-xs mb-1 text-[#71717a]">
                  <span>{item.name}</span>
                  <span style={{ color: item.color }}>{item.value}%</span>
                </div>
                <div className="h-2 bg-[#09090b] w-full overflow-hidden">
                  <div 
                    className="h-full transition-all" 
                    style={{ 
                      width: `${item.value}%`,
                      backgroundColor: item.color
                    }} 
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </TerminalCard>

      {/* Performance Metrics */}
      <TerminalCard title="MODEL_PERFORMANCE" status="active" className="h-[250px] sm:h-[300px]">
        {isLoading ? (
          <div className="h-full flex items-center justify-center text-[#71717a]">
            <Activity className="w-8 h-8 animate-pulse" />
          </div>
        ) : (
          <div className="space-y-4">
            <div className="border-b border-[#27272a] pb-3">
              <div className="text-xs text-[#71717a] mb-1">ENSEMBLE ACCURACY</div>
              <div className="text-xl sm:text-2xl font-bold text-[#00ff9d]">96.8%</div>
            </div>
            <div className="border-b border-[#27272a] pb-3">
              <div className="text-xs text-[#71717a] mb-1">PRECISION</div>
              <div className="text-lg sm:text-xl font-bold text-[#00ff9d]">94.1%</div>
            </div>
            <div>
              <div className="text-xs text-[#71717a] mb-1">RECALL</div>
              <div className="text-lg sm:text-xl font-bold text-[#00ff9d]">93.5%</div>
            </div>
          </div>
        )}
      </TerminalCard>
    </div>
  );
}
