'use client';

import React, { SelectHTMLAttributes, forwardRef } from 'react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  error?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  label?: string;
  className?: string;
  id?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(({
  options,
  value,
  onChange,
  error,
  placeholder = 'Select an option...',
  required,
  disabled,
  label,
  className = '',
  id,
}, ref) => {
  const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="label">
          {label}
        </label>
      )}
      <select
        ref={ref}
        id={selectId}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`input ${error ? 'input-error' : ''} ${className}`}
        required={required}
        disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={error ? `${selectId}-error` : undefined}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p id={`${selectId}-error`} className="error-message" role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

Select.displayName = 'Select';