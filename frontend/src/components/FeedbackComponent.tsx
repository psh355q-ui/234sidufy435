import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, MessageSquare, Send } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';

// API call function normally lives in services/api.ts, but defining here for self-containment during dev
const submitFeedback = async (data: { targetType: string; targetId: string | number; feedback: 'good' | 'bad'; comment?: string }) => {
    const response = await axios.post('/api/feedback', data);
    return response.data;
};

interface FeedbackComponentProps {
    targetType: 'signal' | 'order' | 'report' | 'decision';
    targetId: string | number;
    initialFeedback?: 'good' | 'bad' | null;
    compact?: boolean;
}

export const FeedbackComponent: React.FC<FeedbackComponentProps> = ({
    targetType,
    targetId,
    initialFeedback = null,
    compact = false
}) => {
    const [feedback, setFeedback] = useState<'good' | 'bad' | null>(initialFeedback);
    const [showComment, setShowComment] = useState(false);
    const [comment, setComment] = useState('');

    const mutation = useMutation({
        mutationFn: submitFeedback,
        onSuccess: (data) => {
            // Optimistically updated local state
            setShowComment(false);
            setComment('');
            // You might want to toast success here
        },
        onError: (error) => {
            console.error('Failed to submit feedback', error);
            // Toast error
        }
    });

    const handleVote = (vote: 'good' | 'bad') => {
        if (feedback === vote) {
            // Toggle off if clicking same
            setFeedback(null);
        } else {
            setFeedback(vote);
            mutation.mutate({ targetType, targetId, feedback: vote });
        }
    };

    const handleCommentSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!feedback) return; // Should have a vote to comment
        mutation.mutate({ targetType, targetId, feedback, comment });
    };

    if (compact) {
        return (
            <div className="flex items-center space-x-2">
                <button
                    onClick={() => handleVote('good')}
                    className={`p-1 rounded transition-colors ${feedback === 'good' ? 'text-green-600 bg-green-50' : 'text-gray-400 hover:text-green-600'}`}
                    title="Good decision"
                >
                    <ThumbsUp size={16} fill={feedback === 'good' ? "currentColor" : "none"} />
                </button>
                <button
                    onClick={() => handleVote('bad')}
                    className={`p-1 rounded transition-colors ${feedback === 'bad' ? 'text-red-600 bg-red-50' : 'text-gray-400 hover:text-red-600'}`}
                    title="Bad decision"
                >
                    <ThumbsDown size={16} fill={feedback === 'bad' ? "currentColor" : "none"} />
                </button>
            </div>
        );
    }

    return (
        <div className="mt-4 border-t pt-4">
            <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-500">AI Feedback:</span>
                <div className="flex items-center space-x-3">
                    <button
                        onClick={() => handleVote('good')}
                        className={`flex items-center space-x-1 px-3 py-1.5 rounded-full border transition-all ${feedback === 'good'
                                ? 'border-green-200 bg-green-50 text-green-700'
                                : 'border-gray-200 text-gray-500 hover:border-green-200 hover:text-green-600'
                            }`}
                    >
                        <ThumbsUp size={16} fill={feedback === 'good' ? "currentColor" : "none"} />
                        <span>Good</span>
                    </button>
                    <button
                        onClick={() => handleVote('bad')}
                        className={`flex items-center space-x-1 px-3 py-1.5 rounded-full border transition-all ${feedback === 'bad'
                                ? 'border-red-200 bg-red-50 text-red-700'
                                : 'border-gray-200 text-gray-500 hover:border-red-200 hover:text-red-600'
                            }`}
                    >
                        <ThumbsDown size={16} fill={feedback === 'bad' ? "currentColor" : "none"} />
                        <span>Bad</span>
                    </button>
                    <button
                        onClick={() => setShowComment(!showComment)}
                        className={`p-2 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600 ${showComment ? 'bg-gray-100 text-gray-600' : ''}`}
                    >
                        <MessageSquare size={18} />
                    </button>
                </div>
            </div>

            {showComment && (
                <form onSubmit={handleCommentSubmit} className="mt-3 flex items-start gap-2">
                    <input
                        type="text"
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Tell the AI why..."
                        className="flex-1 text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        autoFocus
                    />
                    <button
                        type="submit"
                        disabled={mutation.isPending || !feedback}
                        className="p-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        <Send size={16} />
                    </button>
                </form>
            )}
        </div>
    );
};
