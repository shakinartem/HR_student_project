import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-xl text-sm font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 disabled:pointer-events-none disabled:opacity-50 transform active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary: "bg-accent text-white shadow-button hover:shadow-buttonHover hover:bg-accent-hover",
        secondary: "bg-bg-secondary text-text-primary ring-1 ring-border hover:bg-bg-card",
        ghost: "bg-transparent text-text-secondary hover:text-text-primary",
        destructive: "bg-red-600 text-white shadow-button hover:bg-red-700",
      },
      size: {
        default: "min-h-12 px-5 py-3",
        lg: "min-h-14 px-6 py-4 text-base",
        sm: "min-h-9 px-3 py-2 text-xs",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}
