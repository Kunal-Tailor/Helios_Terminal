import React, { useEffect, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    primaryColor: '#EDE6DC',
    primaryTextColor: '#2A2724',
    primaryBorderColor: '#DDD5C9',
    lineColor: '#3FA7B3',
    secondaryColor: '#F7F3EE',
    tertiaryColor: '#F7F3EE',
    fontFamily: '"Inter", sans-serif',
  },
  flowchart: {
    curve: 'basis'
  }
});

export const Mermaid: React.FC<{ chart: string; className?: string }> = ({ chart, className = '' }) => {
  const [svg, setSvg] = useState('');

  useEffect(() => {
    let isMounted = true;
    const id = `mermaid-chart-${Math.random().toString(36).substr(2, 9)}`;
    mermaid.render(id, chart).then((result) => {
      if (isMounted) {
        setSvg(result.svg);
      }
    }).catch(e => console.error(e));
    return () => { isMounted = false; };
  }, [chart]);

  return (
    <div 
      className={`w-full flex justify-center [&_svg]:max-w-full [&_svg]:h-auto ${className}`} 
      dangerouslySetInnerHTML={{ __html: svg }} 
    />
  );
};
