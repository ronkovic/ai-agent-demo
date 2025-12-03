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
    <div className="flex h-full flex-col bg-gray-50 dark:bg-gray-900">
      <Header title="設定" />
      <div className="flex flex-1 overflow-hidden">
        <nav className="w-64 border-r bg-white p-4 dark:border-gray-800 dark:bg-gray-950">
          <ul className="space-y-1">
            {settingsNav.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <li key={item.href}>
                  <button
                    onClick={() => router.push(item.href)}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
                        : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
