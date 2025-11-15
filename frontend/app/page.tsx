'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, TrendingUp, BookOpen, PieChart, Shield, Zap } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">Vibe Journal</span>
          </div>
          <div className="flex items-center space-x-2">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-24 md:py-32">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="inline-block">
            <div className="inline-flex items-center rounded-full border border-border px-3 py-1 text-sm">
              <span className="mr-2 h-2 w-2 rounded-full bg-green-500"></span>
              New: Advanced analytics for Indian markets
            </div>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            The Foundation for your
            <span className="block mt-2">Trading Success</span>
          </h1>

          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            A beautifully designed trading journal for Indian markets. Track your trades,
            analyze performance, and build consistent trading habits. Start here then make it your own.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/register">
              <Button size="lg" className="w-full sm:w-auto">
                Get Started
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                View Demo
              </Button>
            </Link>
          </div>

          <p className="text-sm text-muted-foreground">
            Open Source. Built for NSE/BSE traders.
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-24 border-t border-border">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything you need to trade better</h2>
            <p className="text-lg text-muted-foreground">
              Powerful features designed for serious traders
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="border-border">
              <CardHeader>
                <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center mb-4">
                  <TrendingUp className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Track Every Trade</CardTitle>
                <CardDescription>
                  Record entry/exit prices, position sizes, and P&L for every trade in INR
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border">
              <CardHeader>
                <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center mb-4">
                  <BarChart3 className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Advanced Analytics</CardTitle>
                <CardDescription>
                  Win rates, profit factors, risk/reward ratios, and performance metrics
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border">
              <CardHeader>
                <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center mb-4">
                  <PieChart className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Multiple Portfolios</CardTitle>
                <CardDescription>
                  Organize trades across different strategies and portfolios
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border">
              <CardHeader>
                <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center mb-4">
                  <BookOpen className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Notes & Screenshots</CardTitle>
                <CardDescription>
                  Document your trading setup with notes, tags, and chart screenshots
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border">
              <CardHeader>
                <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Secure & Private</CardTitle>
                <CardDescription>
                  JWT authentication, role-based access, and secure data storage
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border">
              <CardHeader>
                <div className="h-12 w-12 rounded-md bg-primary/10 flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Built for Speed</CardTitle>
                <CardDescription>
                  Fast, modern tech stack with Next.js, FastAPI, and SQLite
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Indian Markets Section */}
      <section className="container mx-auto px-4 py-24 border-t border-border">
        <div className="max-w-4xl mx-auto">
          <Card className="border-border bg-card/50">
            <CardContent className="p-12">
              <div className="flex items-center justify-center mb-6">
                <div className="text-4xl">🇮🇳</div>
              </div>
              <h2 className="text-3xl font-bold text-center mb-4">
                Designed for Indian Markets
              </h2>
              <p className="text-lg text-muted-foreground text-center mb-6">
                Built with Indian traders in mind. All amounts in INR (₹), support for NSE/BSE stocks,
                and number formatting that follows the Indian numbering system.
              </p>
              <div className="flex flex-wrap justify-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span>INR Currency</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span>NSE/BSE Support</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span>Lakhs & Crores</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-24 border-t border-border">
        <div className="max-w-3xl mx-auto text-center space-y-8">
          <h2 className="text-4xl md:text-5xl font-bold">
            Ready to improve your trading?
          </h2>
          <p className="text-xl text-muted-foreground">
            Join traders who are building consistent, profitable habits with Vibe Journal
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/register">
              <Button size="lg" className="w-full sm:w-auto">
                Create Free Account
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center space-x-2">
              <div className="h-6 w-6 rounded-md bg-primary flex items-center justify-center">
                <BookOpen className="h-4 w-4 text-primary-foreground" />
              </div>
              <span className="font-semibold">Vibe Journal</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 Vibe Journal. Built for Indian traders.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
