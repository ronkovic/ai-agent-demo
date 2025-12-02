"use client";

import { useTheme } from "next-themes";
import { useEffect, useRef, useState } from "react";
import { Sun, Moon, Monitor } from "lucide-react";
import { Button } from "@/components/ui/Button";

const THEME_ORDER = ["system", "light", "dark"] as const;
type ThemeType = (typeof THEME_ORDER)[number];

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const mountedRef = useRef(false);

  // Avoid hydration mismatch
  useEffect(() => {
    if (!mountedRef.current) {
      mountedRef.current = true;
      // Use requestAnimationFrame to defer state update
      requestAnimationFrame(() => {
        setMounted(true);
      });
      // Initialize localStorage if not set
      const storedTheme = localStorage.getItem("theme");
      if (!storedTheme) {
        localStorage.setItem("theme", "system");
      }
    }
  }, []);

  const cycleTheme = () => {
    const currentIndex = THEME_ORDER.indexOf(theme as ThemeType);
    const nextIndex = (currentIndex + 1) % THEME_ORDER.length;
    const nextTheme = THEME_ORDER[nextIndex];
    setTheme(nextTheme);
    localStorage.setItem("theme", nextTheme);
  };

  const getIcon = () => {
    if (!mounted) {
      return <Monitor className="h-4 w-4" />;
    }

    switch (theme) {
      case "light":
        return <Sun className="h-4 w-4" />;
      case "dark":
        return <Moon className="h-4 w-4" />;
      default:
        return <Monitor className="h-4 w-4" />;
    }
  };

  const getLabel = () => {
    if (!mounted) return "システム";

    switch (theme) {
      case "light":
        return "ライト";
      case "dark":
        return "ダーク";
      default:
        return "システム";
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={cycleTheme}
      className="h-8 gap-2 px-2"
      aria-label={`テーマ切り替え: 現在${getLabel()}`}
      title={`テーマ: ${getLabel()}`}
    >
      {getIcon()}
      <span className="hidden sm:inline text-xs">{getLabel()}</span>
    </Button>
  );
}
