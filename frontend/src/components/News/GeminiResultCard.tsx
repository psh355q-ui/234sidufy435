import React from 'react';
import { Clock, TrendingUp, TrendingDown, AlertCircle, DollarSign } from 'lucide-react';

interface GeminiArticle {
    title: string;
    url?: string;
    source: string;
    published_date: string;
    summary: string;
    sentiment: string;
    urgency: string;
    market_impact: string;
    tickers: string[];
    actionable: boolean;
    fetched_at: string;
    validation_warning?: string;
}

interface GeminiResultCardProps {
    article: GeminiArticle;
    index: number;
}

export const GeminiResultCard: React.FC<GeminiResultCardProps> = ({ article, index }) => {
    const getSentimentColor = (sentiment: string) => {
        switch (sentiment.toLowerCase()) {
            case 'positive': return 'text-green-600';
            case 'negative': return 'text-red-600';
            case 'neutral': return 'text-gray-600';
            default: return 'text-gray-600';
        }
    };

    const getUrgencyColor = (urgency: string) => {
        switch (urgency.toLowerCase()) {
            case 'critical': return 'text-red-600';
            case 'high': return 'text-orange-600';
            case 'medium': return 'text-yellow-600';
            default: return 'text-gray-600';
        }
    };

    const getImpactColor = (impact: string) => {
        switch (impact.toLowerCase()) {
            case 'bullish': return 'text-green-600';
            case 'bearish': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };

    return (
        <div className="p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border-2 border-purple-200 hover:shadow-lg transition-shadow">
            {/* Timestamp */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex flex-col text-xs text-gray-500">
                    <div className="flex items-center">
                        <Clock size={14} className="mr-1" />
                        <span className="font-semibold mr-2">한국:</span>
                        {new Date(article.fetched_at).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}
                    </div>
                    <div className="flex items-center mt-1">
                        <span className="ml-[18px] font-semibold mr-2">미국:</span>
                        {new Date(article.fetched_at).toLocaleString('en-US', {
                            timeZone: 'America/New_York',
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                        })}
                    </div>
                </div>
                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full font-semibold">
                    Gemini 검색 #{index + 1}
                </span>
            </div>

            {/* Title */}
            <h3 className="font-bold text-lg mb-3 text-gray-900">{article.title}</h3>

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="text-sm">
                    <span className="text-gray-500">감정:</span>
                    <span className={`ml-2 font-semibold ${getSentimentColor(article.sentiment)}`}>
                        {article.sentiment === 'positive' ? '긍정' : article.sentiment === 'negative' ? '부정' : '중립'}
                    </span>
                </div>
                <div className="text-sm">
                    <span className="text-gray-500">긴급도:</span>
                    <span className={`ml-2 font-semibold ${getUrgencyColor(article.urgency)}`}>
                        {article.urgency === 'critical' ? '긴급' : article.urgency === 'high' ? '높음' : article.urgency === 'medium' ? '보통' : '낮음'}
                    </span>
                </div>
                <div className="text-sm">
                    <span className="text-gray-500">영향:</span>
                    <span className={`ml-2 font-semibold ${getImpactColor(article.market_impact)}`}>
                        {article.market_impact === 'bullish' ? '상승' : article.market_impact === 'bearish' ? '하락' : '중립'}
                    </span>
                </div>
                <div className="text-sm">
                    <span className="text-gray-500">행동 가능:</span>
                    <span className={`ml-2 font-semibold ${article.actionable ? 'text-blue-600' : 'text-gray-400'}`}>
                        {article.actionable ? '가능' : '불가'}
                    </span>
                </div>
            </div>

            {/* Tickers */}
            {article.tickers && article.tickers.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                    {article.tickers.map((ticker) => (
                        <span key={ticker} className="px-3 py-1 bg-blue-600 text-white text-sm rounded-full font-semibold">
                            ${ticker}
                        </span>
                    ))}
                </div>
            )}

            {/* Summary */}
            <p className="text-sm text-gray-700 mb-4 leading-relaxed">{article.summary}</p>

            {/* Source & Link */}
            <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">출처: {article.source}</span>
                {article.url && (
                    <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline font-semibold flex items-center gap-1"
                    >
                        원문 보기 →
                    </a>
                )}
            </div>

            {/* Validation Warning */}
            {article.validation_warning && (
                <div className="mt-3 flex items-center gap-2 text-xs text-orange-600 bg-orange-50 p-2 rounded">
                    <AlertCircle size={14} />
                    {article.validation_warning}
                </div>
            )}
        </div>
    );
};
