import { Link } from 'react-router-dom';
import type { ReactNode, ButtonHTMLAttributes } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  to?: string;
  href?: string;
  download?: boolean;
  className?: string;
  children: ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  to,
  href,
  download: isDownload,
  className = '',
  children,
  ...rest
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-sans font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-site-accent focus-visible:ring-offset-2 focus-visible:ring-offset-site-bg disabled:opacity-50 disabled:cursor-not-allowed';

  const sizeStyles = {
    sm: 'px-3.5 py-1.5 text-xs rounded-site',
    md: 'px-5 py-2.5 text-sm rounded-site',
    lg: 'px-6 py-3 text-sm rounded-site',
  }[size];

  const variantStyles = {
    primary:
      'bg-site-accent text-white hover:brightness-110 hover:-translate-y-[1px] active:translate-y-0 active:brightness-95 border border-transparent shadow-none',
    secondary:
      'bg-transparent border border-site-border text-site-text-primary hover:border-site-accent/40 hover:bg-site-accent/[0.04] hover:-translate-y-[1px] active:translate-y-0',
    ghost:
      'bg-transparent text-site-text-secondary hover:text-site-accent p-0 border-none rounded-none underline-offset-4 hover:underline decoration-site-accent/50',
  }[variant];

  const combinedStyles =
    `${baseStyles} ${variantStyles} ${variant !== 'ghost' ? sizeStyles : ''} ${className}`.trim();

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
        className={combinedStyles}
        {...(isDownload ? { download: '' } : { target: '_blank', rel: 'noopener noreferrer' })}
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