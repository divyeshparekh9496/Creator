import "./globals.css";

export const metadata = {
  title: "Creator — AI Anime Sequence Maker",
  description: "Convert stories into stunning anime sequences with AI-powered character development, rich effects, and RL self-improvement.",
  keywords: ["anime", "AI", "Gemini", "animation", "creator"],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" data-theme="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  );
}
