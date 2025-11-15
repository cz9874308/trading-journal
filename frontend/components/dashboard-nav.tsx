'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, FolderKanban, LineChart, Users, LogOut, BookOpen } from 'lucide-react';
import { Button } from './ui/button';
import { useAuthStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { ThemeToggle } from './theme-toggle';

export function DashboardNav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const navItems = [
    {
      title: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      title: 'Portfolios',
      href: '/dashboard/portfolios',
      icon: FolderKanban,
    },
    {
      title: 'Analytics',
      href: '/dashboard/analytics',
      icon: LineChart,
    },
  ];

  if (user?.is_admin) {
    navItems.push({
      title: 'Users',
      href: '/dashboard/users',
      icon: Users,
    });
  }

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-card">
      <div className="flex h-16 items-center justify-between border-b px-6">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center">
            <BookOpen className="h-5 w-5 text-primary-foreground" />
          </div>
          <h1 className="text-xl font-bold">Vibe Journal</h1>
        </div>
        <ThemeToggle />
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  pathname === item.href
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
              >
                <Icon className="h-4 w-4" />
                {item.title}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="border-t p-4">
        <div className="mb-3 px-3">
          <p className="text-sm font-medium">{user?.full_name || user?.username}</p>
          <p className="text-xs text-muted-foreground">{user?.email}</p>
          {user?.is_admin && (
            <span className="mt-1 inline-block rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
              Admin
            </span>
          )}
        </div>
        <Button variant="outline" className="w-full" onClick={handleLogout}>
          <LogOut className="mr-2 h-4 w-4" />
          Logout
        </Button>
      </div>
    </div>
  );
}
