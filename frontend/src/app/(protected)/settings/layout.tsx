"use client";

import { usePathname, useRouter } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { cn } from "@/lib/utils";
import { Key, Lock } from "lucide-react";

const settingsNav = [
  {
    label: "LLM APIキー",
    href: "/settings/llm-keys",
    icon: Key,
  },
  {
    label: "APIキー",
    href: "/settings/api-keys",
    icon: Lock,
  },
];

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="flex h-full flex-col">
      <Header title="設定" />
      <div className="flex flex-1 overflow-hidden">
        <nav className="w-64 border-r border-white/20 bg-white/30 dark:bg-gray-900/30 backdrop-blur-md p-4">
          <ul className="space-y-1">
            {settingsNav.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <li key={item.href}>
                  <button
                    onClick={() => router.push(item.href)}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 group",
                      isActive
                        ? "bg-white/40 dark:bg-white/10 text-primary shadow-sm"
                        : "text-gray-700 dark:text-gray-300 hover:bg-white/20 dark:hover:bg-white/5 hover:translate-x-1"
                    )}
                  >
                    <Icon className={cn("h-4 w-4 transition-transform duration-200 group-hover:scale-110", isActive && "text-primary")} />
                    {item.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
        <main className="flex-1 overflow-y-auto p-8 animate-fade-in">{children}</main>
      </div>
    </div>
  );
}
