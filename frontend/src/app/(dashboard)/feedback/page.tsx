'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { TerminalCard } from '@/components/ui/terminal-card';
import { Terminal, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { submitFeedback } from '@/lib/api';

function FeedbackForm() {
  const searchParams = useSearchParams();
  const [messageId, setMessageId] = useState('');
  const [wasCorrect, setWasCorrect] = useState<boolean | null>(null);
  const [userCorrection, setUserCorrection] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAutoFilled, setIsAutoFilled] = useState(false);

  // Auto-fill message ID from query param
  useEffect(() => {
    // Try searchParams first (Next.js way)
    let id = searchParams.get('id');
    
    // Fallback: read from window.location if searchParams doesn't have it
    if (!id && typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      id = urlParams.get('id');
    }
    
    if (id && id.trim() && !messageId) {
      const cleanId = id.trim();
      setMessageId(cleanId);
      setIsAutoFilled(true);
    }
  }, [searchParams, messageId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!messageId.trim()) {
      toast.error('Message ID is required');
      return;
    }

    if (wasCorrect === null) {
      toast.error('Please indicate if the moderation was correct');
      return;
    }

    setIsSubmitting(true);
    try {
      await submitFeedback({
        message_id: messageId,
        was_correct: wasCorrect,
        user_correction: userCorrection || undefined,
      });
      
      toast.success('Feedback submitted successfully!', {
        description: 'Your feedback helps improve the model.',
      });
      
      // Reset form
      setMessageId('');
      setWasCorrect(null);
      setUserCorrection('');
    } catch (err: any) {
      toast.error('Failed to submit feedback', {
        description: err.message || 'Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto w-full px-2 sm:px-0">
      <TerminalCard title="MLOPS_FEEDBACK_LOOP" status="active">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Message ID Input */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-[#00ff9d] opacity-70">
                <Terminal size={14} />
                <span className="text-xs">root@hate_speech:~/feedback$</span>
              </div>
              {isAutoFilled && (
                <span className="text-xs text-[#00ff9d] border border-[#00ff9d]/30 px-2 py-1">
                  AUTO-FILLED
                </span>
              )}
            </div>
            <input
              type="text"
              value={messageId}
              onChange={(e) => {
                setMessageId(e.target.value);
                setIsAutoFilled(false); // Clear auto-fill indicator when user edits
              }}
              placeholder="// ENTER MESSAGE_ID FROM ANALYSIS..."
              className={`w-full bg-transparent border px-4 py-3 text-[#e4e4e7] font-mono text-sm focus:outline-none transition-colors ${
                isAutoFilled 
                  ? 'border-[#00ff9d]' 
                  : 'border-[#27272a] focus:border-[#00ff9d]'
              }`}
            />
          </div>

          {/* Correct/Incorrect Selection */}
          <div>
            <div className="text-xs text-[#71717a] mb-3 uppercase">VERDICT_ACCURACY</div>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setWasCorrect(true)}
                className={`flex-1 border-2 px-6 py-4 font-bold uppercase transition-all ${
                  wasCorrect === true
                    ? 'border-[#00ff9d] text-[#00ff9d] bg-[#00ff9d]/10'
                    : 'border-[#27272a] text-[#71717a] hover:border-[#00ff9d]/50'
                }`}
              >
                <CheckCircle className="w-5 h-5 mx-auto mb-2" />
                CORRECT
              </button>
              <button
                type="button"
                onClick={() => setWasCorrect(false)}
                className={`flex-1 border-2 px-6 py-4 font-bold uppercase transition-all ${
                  wasCorrect === false
                    ? 'border-[#ff0055] text-[#ff0055] bg-[#ff0055]/10'
                    : 'border-[#27272a] text-[#71717a] hover:border-[#ff0055]/50'
                }`}
              >
                <AlertCircle className="w-5 h-5 mx-auto mb-2" />
                INCORRECT
              </button>
            </div>
          </div>

          {/* User Correction (Optional) */}
          {wasCorrect === false && (
            <div>
              <div className="text-xs text-[#71717a] mb-2 uppercase">CORRECTION_NOTES</div>
              <textarea
                value={userCorrection}
                onChange={(e) => setUserCorrection(e.target.value)}
                placeholder="// ENTER CORRECT ACTION OR NOTES..."
                className="w-full bg-transparent border border-[#27272a] px-4 py-3 text-[#e4e4e7] font-mono text-sm min-h-[100px] resize-none focus:outline-none focus:border-[#00ff9d] transition-colors"
              />
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting || !messageId || wasCorrect === null}
            className={`
              w-full h-12 sm:h-14 lg:h-16 border-2 font-bold tracking-[0.1em] sm:tracking-[0.2em] text-sm sm:text-base lg:text-xl uppercase transition-all
              ${isSubmitting || !messageId || wasCorrect === null
                ? 'border-[#27272a] text-[#27272a] cursor-not-allowed' 
                : 'border-[#00ff9d] text-[#00ff9d] hover:bg-[#00ff9d] hover:text-black shadow-[0_0_20px_rgba(0,255,157,0.2)]'
              }
            `}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 inline mr-2 animate-spin" />
                SUBMITTING...
              </>
            ) : (
              '>> SUBMIT FEEDBACK'
            )}
          </button>
        </form>
      </TerminalCard>
    </div>
  );
}

export default function FeedbackPage() {
  return (
    <Suspense fallback={
      <div className="max-w-4xl mx-auto">
        <TerminalCard title="MLOPS_FEEDBACK_LOOP" status="active">
          <div className="h-64 flex items-center justify-center text-[#71717a]">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
        </TerminalCard>
      </div>
    }>
      <FeedbackForm />
    </Suspense>
  );
}
