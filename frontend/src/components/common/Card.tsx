import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  children: React.ReactNode;
  padding?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  children,
  className = '',
  padding = true,
  ...props
}) => {
  return (
    <div
      className={`bg-white rounded-lg shadow-md ${padding ? 'p-6' : ''} ${className}`}
      {...props}
    >
      {title && <h3 className="text-lg font-semibold mb-4 text-gray-900">{title}</h3>}
      {children}
    </div>
  );
};
