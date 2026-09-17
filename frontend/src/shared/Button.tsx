import React from 'react';
import { Link } from 'react-router-dom';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  to?: string;
  href?: string;
  download?: boolean | string;
  className?: string;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  to,
  href,
  download,
  className = '',
  children,
  ...rest
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-sans font-medium transition-all duration-150 focus:outline-none focus:ring-1 focus:ring-site-accent disabled:opacity-50 disabled:cursor-not-allowed';

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs rounded-site',
    md: 'px-4 py-2 text-sm rounded-site',
    lg: 'px-5 py-2.5 text-base rounded-site',
  }[size];

  const variantStyles = {
    primary: 'bg-site-accent text-white hover:opacity-90 active:scale-[0.99] border border-transparent shadow-none',
    secondary: 'bg-transparent border border-site-border text-site-text-primary hover:border-site-text-secondary hover:bg-site-surface/50 active:scale-[0.99]',
    ghost: 'bg-transparent text-site-text-secondary hover:text-site-text-primary hover:underline p-0 border-none rounded-none',
  }[variant];

  const combinedStyles = `${baseStyles} ${variantStyles} ${variant !== 'ghost' ? sizeStyles : ''} ${className}`.trim();

  if (to) {
    return (
      <Link to={to} className={combinedStyles}>
        {children}
      </Link>
    );
  }

  if (href) {
    return (
      <a
        href={href}
        download={download}
        className={combinedStyles}
        target={download ? undefined : "_blank"}
        rel={download ? undefined : "noopener noreferrer"}
      >
        {children}
      </a>
    );
  }

  return (
    <button className={combinedStyles} {...rest}>
      {children}
    </button>
  );
};