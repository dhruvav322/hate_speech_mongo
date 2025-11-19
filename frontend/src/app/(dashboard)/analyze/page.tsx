'use client';

import { useState } from 'react';
import Link from 'next/link';
import { TerminalCard } from '@/components/ui/terminal-card';
import { Terminal, Activity, ShieldAlert, AlertTriangle } from 'lucide-react';
import { analyzeText, submitFeedback, type ModerationResponse } from '@/lib/api';
import { toast } from 'sonner';

export default function AnalyzePage() {
  const [inputText, setInputText] = useState('');
  const [analysisResult, setAnalysisResult] = useState<ModerationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Map API action to display action
  const getDisplayAction = (action: string): 'ALLOW' | 'BLOCK' | 'REVIEW' => {
    switch (action) {
      case 'none':
      case 'warn':
        return 'ALLOW';
      case 'hide':
      case 'delete':
      case 'ban':
        return 'BLOCK';
      default:
        return 'REVIEW';
    }
  };

  const handleAnalyze = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to analyze.');
      return;
    }
    setError(null);
    setIsLoading(true);
    setAnalysisResult(null);

    try {
      const data = await analyzeText({
        text: inputText,
      });
      
      setAnalysisResult(data);
      const displayAction = getDisplayAction(data.moderation_action.action);
      toast.success('Analysis Complete!', {
        description: `Content was ${displayAction === 'BLOCK' ? 'blocked' : displayAction === 'REVIEW' ? 'flagged for review' : 'allowed'}.`,
      });
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
      toast.error('Analysis Failed', {
        description: err.message || 'Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Convert toxicity scores to breakdown format
  const getBreakdown = () => {
    if (!analysisResult) return [];
    
    const scores = analysisResult.toxicity_scores;
    return [
      { model: 'TOXIC', score: Math.round(scores.toxic * 100) },
      { model: 'SEVERE', score: Math.round(scores.severe_toxic * 100) },
      { model: 'OBSCENE', score: Math.round(scores.obscene * 100) },
      { model: 'THREAT', score: Math.round(scores.threat * 100) },
      { model: 'INSULT', score: Math.round(scores.insult * 100) },
      { model: 'IDENTITY', score: Math.round(scores.identity_hate * 100) },
    ];
  };

  // Highlight toxic words in text
  const highlightToxicWords = (text: string) => {
    // Common toxic keywords (can be enhanced with ML-based detection)
    const toxicKeywords = [
      'stupid', 'idiot', 'hate', 'kill', 'die', 'ugly', 'worthless', 'garbage',
      'bitch', 'ass', 'fuck', 'shit', 'damn', 'hell', 'crap', 'bastard',
      'moron', 'retard', 'dumb', 'fool', 'loser', 'pathetic', 'disgusting'
    ];
    
    const words = text.split(/(\s+)/);
    return words.map((word, index) => {
      const lowerWord = word.toLowerCase().replace(/[^\w]/g, '');
      const isToxic = toxicKeywords.some(keyword => lowerWord.includes(keyword));
      
      if (isToxic) {
        return (
          <span key={index} className="bg-[#ff0055]/30 text-[#ff0055] font-bold px-1 rounded">
            {word}
          </span>
        );
      }
      return <span key={index}>{word}</span>;
    });
  };

  const displayAction = analysisResult ? getDisplayAction(analysisResult.moderation_action.action) : null;
  const status = displayAction === 'BLOCK' ? 'danger' : displayAction === 'ALLOW' ? 'success' : 'idle';

  return (
    <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8 h-full w-full">
      
      {/* LEFT COLUMN: INPUT TERMINAL */}
      <div className="lg:col-span-2 flex flex-col gap-6">
        <TerminalCard title="INPUT_STREAM // TEXT_DATA" status="active" className="h-2/3">
          <div className="relative h-full flex flex-col">
            <div className="flex items-center gap-2 text-[#00ff9d] mb-2 opacity-70">
              <Terminal size={14} />
              <span className="text-xs">root@hate_speech:~/input_stream$</span>
            </div>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 bg-transparent border-none outline-none text-[#e4e4e7] font-mono text-sm sm:text-base lg:text-lg resize-none placeholder:text-[#27272a]"
              placeholder="// ENTER SUSPECT DATA FOR ANALYSIS..."
              spellCheck={false}
            />
            
            {/* Preset Commands */}
            <div className="mt-4 flex gap-2 border-t border-[#27272a] pt-4">
              <button 
                onClick={() => setInputText('You are stupid and I hate you')} 
                className="text-xs text-[#71717a] hover:text-[#00ff9d] hover:bg-[#09090b] px-2 py-1 border border-[#27272a] transition-colors"
              >
                ./load_sample --toxic
              </button>
              <button 
                onClick={() => setInputText('Have a nice day everyone')} 
                className="text-xs text-[#71717a] hover:text-[#00ff9d] hover:bg-[#09090b] px-2 py-1 border border-[#27272a] transition-colors"
              >
                ./load_sample --safe
              </button>
            </div>
          </div>
        </TerminalCard>

        {/* ACTION BUTTON */}
        <button
          onClick={handleAnalyze}
          disabled={isLoading}
          className={`
            h-12 sm:h-14 lg:h-16 w-full border-2 font-bold tracking-[0.1em] sm:tracking-[0.2em] text-sm sm:text-base lg:text-xl uppercase transition-all
            ${isLoading 
              ? 'border-[#27272a] text-[#27272a] cursor-not-allowed' 
              : 'border-[#00ff9d] text-[#00ff9d] hover:bg-[#00ff9d] hover:text-black shadow-[0_0_20px_rgba(0,255,157,0.2)]'
            }
          `}
        >
          {isLoading ? '>> EXECUTING PROTOCOLS...' : '>> INITIATE SCAN'}
        </button>
      </div>

      {/* RIGHT COLUMN: INTELLIGENCE REPORT */}
      <div className="flex flex-col gap-6">
        <TerminalCard 
          title="THREAT_ANALYSIS" 
          className="h-full" 
          status={status}
        >
          {!analysisResult && !isLoading && (
            <div className="h-full flex flex-col items-center justify-center text-[#27272a] gap-4">
              <Activity className="w-12 h-12 animate-pulse opacity-20" />
              <p className="text-sm tracking-widest">AWAITING DATA...</p>
            </div>
          )}

          {isLoading && (
            <div className="h-full flex flex-col gap-2 font-mono text-xs text-[#00ff9d]">
              <p>&gt; Connecting to Neural Engine...</p>
              <p>&gt; Loading BERT weights [==========] 100%</p>
              <p>&gt; Analyzing semantic vector...</p>
              <p className="animate-pulse">&gt; CALCULATING PROBABILITY...</p>
            </div>
          )}

          {analysisResult && !isLoading && (
            <div className="flex flex-col gap-6">
              {/* Verdict Display */}
              <div className={`border p-4 text-center ${displayAction === 'BLOCK' ? 'border-[#ff0055] text-[#ff0055]' : 'border-[#00ff9d] text-[#00ff9d]'}`}>
                <div className="text-sm opacity-70 mb-1">VERDICT</div>
                <div className={`text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tighter ${displayAction === 'BLOCK' ? 'text-shadow-danger' : 'text-shadow-glow'}`}>
                  {displayAction}
                </div>
              </div>

              {/* Score Visualization */}
              <div>
                <div className="flex justify-between text-xs mb-2 text-[#a1a1aa]">
                  <span>TOXICITY_LEVEL</span>
                  <span>{(analysisResult.overall_score * 100).toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-[#09090b] w-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-500 ${analysisResult.overall_score > 0.5 ? 'bg-[#ff0055]' : 'bg-[#00ff9d]'}`} 
                    style={{ width: `${analysisResult.overall_score * 100}%` }} 
                  />
                </div>
              </div>

              {/* Ensemble Breakdown */}
              <div className="space-y-3 border-t border-[#27272a] pt-4">
                <div className="text-xs text-[#71717a] uppercase">Ensemble Logic</div>
                {getBreakdown().map((item) => (
                  <div key={item.model} className="flex items-center justify-between text-sm">
                    <span className="text-[#e4e4e7]">{item.model}</span>
                    <span className={item.score > 50 ? 'text-[#ff0055]' : 'text-[#00ff9d]'}>
                      {item.score}%
                    </span>
                  </div>
                ))}
              </div>

              {/* Confidence & Reason */}
              <div className="space-y-2 border-t border-[#27272a] pt-4">
                <div className="text-xs text-[#71717a] uppercase">Confidence</div>
                <div className="text-sm text-[#00ff9d]">
                  {(analysisResult.moderation_action.confidence * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-[#71717a] mt-2">
                  {analysisResult.moderation_action.reason}
                </div>
              </div>

              {/* Highlighted Text Analysis */}
              {inputText && (
                <div className="space-y-2 border-t border-[#27272a] pt-4">
                  <div className="text-xs text-[#71717a] uppercase">Text Analysis</div>
                  <div className="text-sm text-[#e4e4e7] font-mono p-3 bg-[#09090b] border border-[#27272a] rounded">
                    {highlightToxicWords(inputText)}
                  </div>
                </div>
              )}

              {/* Report Error Button */}
              {analysisResult?.message_id && (
                <Link 
                  href={`/feedback?id=${encodeURIComponent(analysisResult.message_id)}`}
                  className="mt-4 w-full border-2 border-[#ff0055] text-[#ff0055] hover:bg-[#ff0055] hover:text-black font-bold tracking-widest text-sm uppercase px-4 py-3 transition-all flex items-center justify-center gap-2"
                >
                  <AlertTriangle size={16} />
                  REPORT ERROR
                </Link>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 border border-[#ff0055] text-[#ff0055] text-xs">
              <ShieldAlert size={14} className="inline mr-2" />
              ERROR: {error}
            </div>
          )}
        </TerminalCard>
      </div>
    </div>
  );
}
