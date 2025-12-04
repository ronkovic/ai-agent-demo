import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { UserMenu } from "@/components/layout/UserMenu";
import { cn } from "@/lib/utils";

interface HeaderProps {
  title?: string;
  showBackButton?: boolean;
  onBack?: () => void;
  className?: string;
  showThemeToggle?: boolean;
  showUserMenu?: boolean;
  children?: React.ReactNode;
}

export function Header({
  title,
  showBackButton,
  onBack,
  className,
  showThemeToggle = true,
  showUserMenu = true,
  children,
}: HeaderProps) {
  return (
    <header
      className={cn(
        "hidden md:flex h-14 items-center justify-between border-b border-white/20 bg-white/30 px-4 dark:bg-gray-900/30 backdrop-blur-md",
        className
      )}
    >
      <div className="flex items-center gap-4">
        {showBackButton && (
          <Button
            variant="outline"
            size="sm"
            onClick={onBack}
            className="h-8 w-8 p-0"
            aria-label="Go back"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
        )}
        {title && (
          <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {title}
          </h1>
        )}
        {children}
      </div>
      <div className="flex items-center gap-2">
        {showThemeToggle && <ThemeToggle />}
        {showUserMenu && <UserMenu />}
      </div>
    </header>
  );
}
