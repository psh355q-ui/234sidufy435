/**
 * LoadingSpinner.tsx - 로딩 애니메이션 컴포넌트
 * 
 * 📊 Data Sources:
 *   - Props: size (선택) - 스피너 크기
 *   - No external data
 * 
 * 🔗 Dependencies:
 *   - react
 *   - Tailwind CSS: 애니메이션
 * 
 * 📤 Props:
 *   - size?: 'sm' | 'md' | 'lg' - 스피너 크기 (default: md)
 * 
 * 🔄 Used By:
 *   - 모든 데이터 로딩 페이지
 *   - API 호출 중 표시
 * 
 * 📝 Notes:
 *   - CSS spin animation 사용
 *   - 3가지 크기 지원 (sm/md/lg)
 */

import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  className = '',
}) => {
  const sizeMap = {
    sm: 16,
    md: 24,
    lg: 32,
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Loader2 className="animate-spin text-blue-600" size={sizeMap[size]} />
    </div>
  );
};
