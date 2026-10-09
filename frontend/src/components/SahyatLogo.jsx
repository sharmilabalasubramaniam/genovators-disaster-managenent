import React from 'react';

export default function SahyatLogo({ variant = 'full', className = '' }) {
  // We use the exact user-uploaded image for all variants to ensure perfect brand consistency.
  let sizeClasses = "w-full max-w-[200px]"; // default for 'full'
  
  if (variant === 'login') {
    sizeClasses = "w-full max-w-[250px] mb-4";
  } else if (variant === 'icon' || variant === 'compact') {
    sizeClasses = "w-16 h-auto";
  } else if (variant === 'light') {
    sizeClasses = "w-full max-w-[180px] rounded-lg overflow-hidden"; // Ensure it looks neat if it has a white bg on dark sidebar
  }

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <img 
        src="/assets/logo-final.png" 
        alt="Sahyat Logo" 
        className={sizeClasses} 
      />
    </div>
  );
}
