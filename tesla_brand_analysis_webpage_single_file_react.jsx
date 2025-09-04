import React, { useMemo, useState } from "react";
import { CheckCircle, XCircle, Link as LinkIcon, ShieldCheck, Timer, Globe, Users, TrendingUp, AlertTriangle, Search, Filter, BarChart3, PieChart as PieIcon, Star } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Bar, BarChart, XAxis, YAxis, CartesianGrid } from "recharts";

// Single-file, drop-in React page. TailwindCSS recommended for styling.
// Default export is required by the canvas preview.

const RAW = {
  "status": "success",
  "brand_analysis": {
    "brand_name": "Tesla",
    "website": "https://www.tesla.com/",
    "analysis_date": "2025-08-28T15:04:31.442279",
    "processing_time": "Real-time SERP + GPT-4o analysis",
    "analysis_method": "SerpAPI + GPT-4o with follower tracking"
  },
  "data": {
    "platforms": [
      {
        "name": "Google Business",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on Google Business.",
        "activity_level": "unknown"
      },
      {
        "name": "LinkedIn",
        "found": true,
        "verified": true,
        "profile_url": "https://www.linkedin.com/company/tesla-motors",
        "confidence": "high",
        "search_ranking": 1,
        "followers_count": 12261045,
        "subscribers_count": null,
        "engagement_level": "high",
        "posts_count": null,
        "verification_badge": "verified",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 90,
        "notes": "Official Tesla LinkedIn profile with over 12 million followers. Verified account.",
        "activity_level": "unknown"
      },
      {
        "name": "YouTube",
        "found": true,
        "verified": true,
        "profile_url": "https://www.youtube.com/channel/UC5WjFrtBdufl6CZojX3D8dQ",
        "confidence": "high",
        "search_ranking": 1,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "high",
        "posts_count": null,
        "verification_badge": "verified",
        "account_age_estimate": "unknown",
        "last_activity": "recent",
        "profile_completeness": 80,
        "notes": "Official Tesla YouTube channel. Verified with regular content updates.",
        "activity_level": "high"
      },
      {
        "name": "TikTok",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on TikTok.",
        "activity_level": "unknown"
      },
      {
        "name": "Instagram",
        "found": true,
        "verified": true,
        "profile_url": "https://www.instagram.com/teslamotors/",
        "confidence": "high",
        "search_ranking": 1,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "high",
        "posts_count": null,
        "verification_badge": "verified",
        "account_age_estimate": "unknown",
        "last_activity": "recent",
        "profile_completeness": 85,
        "notes": "Official Tesla Instagram profile. Verified with active engagement.",
        "activity_level": "high"
      },
      {
        "name": "Pinterest",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on Pinterest.",
        "activity_level": "unknown"
      },
      {
        "name": "X (Twitter)",
        "found": true,
        "verified": true,
        "profile_url": "https://x.com/teslaownerssv",
        "confidence": "medium",
        "search_ranking": 1,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "high",
        "posts_count": null,
        "verification_badge": "verified",
        "account_age_estimate": "unknown",
        "last_activity": "recent",
        "profile_completeness": 70,
        "notes": "Tesla Owners Silicon Valley is a prominent Tesla-related account. Verified.",
        "activity_level": "high"
      },
      {
        "name": "Facebook",
        "found": true,
        "verified": false,
        "profile_url": "https://www.facebook.com/TeslaMotorsCorp/",
        "confidence": "medium",
        "search_ranking": 1,
        "followers_count": 278870,
        "subscribers_count": null,
        "engagement_level": "medium",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 60,
        "notes": "Tesla fan page with significant following but not verified.",
        "activity_level": "medium"
      },
      {
        "name": "Medium",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on Medium.",
        "activity_level": "unknown"
      },
      {
        "name": "Tumblr",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on Tumblr.",
        "activity_level": "unknown"
      },
      {
        "name": "Threads",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on Threads.",
        "activity_level": "unknown"
      },
      {
        "name": "Quora",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on Quora.",
        "activity_level": "unknown"
      },
      {
        "name": "Reddit",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on Reddit.",
        "activity_level": "unknown"
      },
      {
        "name": "Blue Sky",
        "found": false,
        "verified": null,
        "profile_url": null,
        "confidence": "low",
        "search_ranking": null,
        "followers_count": null,
        "subscribers_count": null,
        "engagement_level": "unknown",
        "posts_count": null,
        "verification_badge": "none",
        "account_age_estimate": "unknown",
        "last_activity": "unknown",
        "profile_completeness": 0,
        "notes": "No official Tesla profile found on Blue Sky.",
        "activity_level": "unknown"
      }
    ],
    "summary": {
      "total_platforms_checked": 14,
      "platforms_found": 5,
      "platforms_missing": 9,
      "completion_percentage": 35.71,
      "verification_rate": 60,
      "average_search_ranking": 1,
      "total_followers": 12539915,
      "average_engagement": "medium",
      "verified_accounts": 3
    }
  },
  "competitor_analysis": {},
  "insights": {
    "digital_presence_score": "B-",
    "final_score": 66.7,
    "strongest_presence": "LinkedIn",
    "biggest_opportunity": "Google Business",
    "total_followers": 12539915,
    "average_engagement": "high",
    "verification_gaps": 1,
    "industry_benchmark": "Below average (36% vs 52% industry average)",
    "recommendations": [
      {
        "platform": "Google Business",
        "priority": "medium",
        "reason": "Critical for local SEO and customer reviews",
        "estimated_setup_time": "2-4 hours",
        "potential_reach": "Local search dominance"
      },
      {
        "platform": "TikTok",
        "priority": "high",
        "reason": "Fastest-growing platform for viral marketing and reaching Gen Z/Millennial audiences",
        "estimated_setup_time": "1-2 hours",
        "potential_reach": "500K+ monthly views potential"
      },
      {
        "platform": "Pinterest",
        "priority": "medium",
        "reason": "Perfect for visual discovery and driving website traffic",
        "estimated_setup_time": "2-3 hours",
        "potential_reach": "50K+ monthly pin impressions"
      }
    ]
  },
  "meta": {
    "analyzer_version": "2.1 Pro Enhanced",
    "platforms_supported": 14,
    "analysis_method": "Real-time SERP search + GPT-4o analysis",
    "model": "GPT-4o",
    "serp_provider": "serpapi",
    "features": [
      "live_verification",
      "actual_urls",
      "search_rankings",
      "follower_counts",
      "engagement_metrics",
      "verification_badges",
      "account_age_estimation",
      "profile_completeness",
      "follower_weighted_scoring",
      "competitor_analysis",
      "actionable_insights"
    ]
  }
};

const COLORS = ["#60A5FA", "#34D399", "#FBBF24", "#F87171", "#A78BFA", "#F472B6", "#22D3EE", "#F59E0B"]; // Tailwind palette-ish

function Badge({ children, intent = "neutral" }) {
  const map = {
    success: "bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-400/30",
    danger: "bg-rose-500/20 text-rose-300 ring-1 ring-rose-400/30",
    warn: "bg-amber-500/20 text-amber-200 ring-1 ring-amber-400/30",
    info: "bg-sky-500/20 text-sky-200 ring-1 ring-sky-400/30",
    neutral: "bg-zinc-700/40 text-zinc-200 ring-1 ring-white/5",
  };
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${map[intent]}`}>{children}</span>
  );
}

function Stat({ icon: Icon, label, value, hint }) {
  return (
    <div className="rounded-2xl bg-zinc-900/80 backdrop-blur p-4 shadow-xl ring-1 ring-white/10">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-zinc-400 text-xs uppercase tracking-wider">{label}</p>
          <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
          {hint && <p className="text-zinc-400 text-xs mt-1">{hint}</p>}
        </div>
        <div className="p-2 rounded-xl bg-zinc-800/60 ring-1 ring-white/10">
          <Icon className="h-5 w-5 text-zinc-200" />
        </div>
      </div>
    </div>
  );
}

function Progress({ value }) {
  return (
    <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden ring-1 ring-white/10">
      <div className="h-full bg-sky-500" style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
    </div>
  );
}

function PlatformCard({ p }) {
  const found = p.found;
  const verified = p.verified === true;
  const notFound = p.found === false;
  const statusIntent = found ? (verified ? "success" : "info") : "danger";
  const engagementMap = {
    high: "High",
    medium: "Medium",
    low: "Low",
    unknown: "Unknown",
  };

  return (
    <div className="group rounded-2xl bg-zinc-950/70 backdrop-blur hover:bg-zinc-950/90 transition-colors shadow-2xl ring-1 ring-white/10 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          {found ? (
            <CheckCircle className="h-5 w-5 text-emerald-400" />
          ) : (
            <XCircle className="h-5 w-5 text-rose-400" />
          )}
          <h3 className="text-white font-semibold text-base">{p.name}</h3>
        </div>
        <Badge intent={statusIntent}>{found ? (verified ? "Verified" : "Found") : "Missing"}</Badge>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
        <div className="flex items-center gap-2 text-zinc-300"><Globe className="h-4 w-4"/>Rank: {p.search_ranking ?? "-"}</div>
        <div className="flex items-center gap-2 text-zinc-300"><Users className="h-4 w-4"/>Followers: {p.followers_count ?? p.subscribers_count ?? "-"}</div>
        <div className="flex items-center gap-2 text-zinc-300"><TrendingUp className="h-4 w-4"/>Engagement: {engagementMap[p.engagement_level] ?? p.engagement_level}</div>
        <div className="flex items-center gap-2 text-zinc-300"><Star className="h-4 w-4"/>Profile completeness: {p.profile_completeness ?? 0}%</div>
      </div>

      <div className="mt-3 flex items-center gap-2">
        {p.profile_url ? (
          <a href={p.profile_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sky-300 hover:text-sky-200 text-sm">
            <LinkIcon className="h-4 w-4"/> Visit profile
          </a>
        ) : (
          <span className="inline-flex items-center gap-1 text-zinc-500 text-sm"><AlertTriangle className="h-4 w-4"/> No URL</span>
        )}
        {verified && <span className="inline-flex items-center gap-1 text-emerald-300 text-sm"><ShieldCheck className="h-4 w-4"/> Verified</span>}
        {p.last_activity && <span className="inline-flex items-center gap-1 text-zinc-400 text-sm"><Timer className="h-4 w-4"/>Last: {p.last_activity}</span>}
      </div>

      {p.notes && <p className="mt-3 text-xs text-zinc-400 leading-relaxed">{p.notes}</p>}
    </div>
  );
}

function Section({ title, icon: Icon, right }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="p-2 rounded-xl bg-zinc-900 ring-1 ring-white/10"><Icon className="h-4 w-4 text-zinc-200"/></div>
        <h2 className="text-lg md:text-xl font-semibold text-white">{title}</h2>
      </div>
      {right}
    </div>
  );
}

export default function BrandAnalysisPage() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all"); // all | found | missing
  const [sort, setSort] = useState("default"); // default | followers | completeness | name

  const platforms = RAW.data.platforms;
  const summary = RAW.data.summary;
  const insights = RAW.insights;
  const brand = RAW.brand_analysis;

  const filtered = useMemo(() => {
    let arr = [...platforms];
    if (filter === "found") arr = arr.filter(p => p.found);
    if (filter === "missing") arr = arr.filter(p => p.found === false);
    if (query.trim()) {
      const q = query.toLowerCase();
      arr = arr.filter(p => `${p.name} ${p.notes ?? ""}`.toLowerCase().includes(q));
    }
    if (sort === "followers") arr.sort((a,b) => (b.followers_count ?? b.subscribers_count ?? -1) - (a.followers_count ?? a.subscribers_count ?? -1));
    if (sort === "completeness") arr.sort((a,b) => (b.profile_completeness ?? 0) - (a.profile_completeness ?? 0));
    if (sort === "name") arr.sort((a,b) => a.name.localeCompare(b.name));
    return arr;
  }, [platforms, filter, query, sort]);

  const foundCount = platforms.filter(p => p.found).length;
  const missingCount = platforms.length - foundCount;

  const pieData = [
    { name: "Found", value: foundCount },
    { name: "Missing", value: missingCount },
  ];

  const followerBars = platforms
    .map(p => ({ name: p.name, followers: p.followers_count ?? p.subscribers_count ?? 0 }))
    .filter(d => d.followers > 0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-950 to-black text-zinc-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2">
              <img src="https://www.tesla.com/themes/custom/tesla_frontend/assets/favicons/favicon.ico" alt="logo" className="h-6 w-6"/>
              <h1 className="text-2xl md:text-3xl font-bold text-white">{brand.brand_name} – Digital Presence Report</h1>
            </div>
            <p className="text-zinc-400 mt-1 text-sm">Website: <a href={brand.website} target="_blank" rel="noreferrer" className="text-sky-300 hover:text-sky-200">{brand.website}</a></p>
            <p className="text-zinc-500 text-xs mt-1">Analyzed on {new Date(brand.analysis_date).toLocaleString()}</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 w-full md:w-auto">
            <Stat icon={Globe} label="Checked" value={summary.total_platforms_checked} hint="Platforms" />
            <Stat icon={CheckCircle} label="Found" value={summary.platforms_found} hint={`${Math.round((foundCount/platforms.length)*100)}% presence`} />
            <Stat icon={ShieldCheck} label="Verified" value={summary.verified_accounts} hint={`${summary.verification_rate}% rate`} />
            <Stat icon={Users} label="Total Followers" value={summary.total_followers.toLocaleString()} hint="across platforms" />
          </div>
        </div>

        {/* Score & Overview */}
        <div className="mt-6 grid md:grid-cols-3 gap-4">
          <div className="rounded-2xl bg-zinc-900/80 p-5 ring-1 ring-white/10 shadow-xl">
            <Section title="Presence Score" icon={PieIcon} />
            <div className="mt-4">
              <div className="flex items-end gap-2">
                <p className="text-4xl font-semibold text-white">{insights.final_score}</p>
                <Badge intent="info">{insights.digital_presence_score}</Badge>
              </div>
              <p className="text-zinc-400 text-sm mt-2">Industry benchmark: {insights.industry_benchmark}</p>
              <div className="mt-3">
                <Progress value={summary.completion_percentage} />
                <p className="text-zinc-400 text-xs mt-1">Profile completion: {summary.completion_percentage}%</p>
              </div>
            </div>
          </div>
          <div className="rounded-2xl bg-zinc-900/80 p-5 ring-1 ring-white/10 shadow-xl">
            <Section title="Found vs Missing" icon={PieIcon} />
            <div className="h-44 mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie dataKey="value" data={pieData} outerRadius={70} label>
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#0a0a0a", border: "1px solid #3f3f46" }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="rounded-2xl bg-zinc-900/80 p-5 ring-1 ring-white/10 shadow-xl">
            <Section title="Followers by Platform" icon={BarChart3} />
            <div className="h-44 mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={followerBars}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis dataKey="name" tick={{ fill: "#a1a1aa" }} interval={0} angle={-20} textAnchor="end" height={50} />
                  <YAxis tick={{ fill: "#a1a1aa" }} />
                  <Tooltip contentStyle={{ background: "#0a0a0a", border: "1px solid #3f3f46" }} />
                  <Bar dataKey="followers">
                    {followerBars.map((_, index) => (
                      <Cell key={`bar-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-8 rounded-2xl bg-zinc-900/80 p-5 ring-1 ring-white/10 shadow-xl">
          <Section title="Actionable Recommendations" icon={TrendingUp} />
          <div className="mt-4 grid md:grid-cols-3 gap-4">
            {RAW.insights.recommendations.map((r, i) => (
              <div key={i} className="rounded-2xl bg-zinc-950/70 ring-1 ring-white/10 p-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-white font-semibold">{r.platform}</h3>
                  <Badge intent={r.priority === 'high' ? 'warn' : 'info'}>Priority: {r.priority}</Badge>
                </div>
                <p className="text-zinc-300 text-sm mt-2">{r.reason}</p>
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-zinc-400">
                  <div className="p-2 rounded-lg bg-zinc-900 ring-1 ring-white/10">Setup: {r.estimated_setup_time}</div>
                  <div className="p-2 rounded-lg bg-zinc-900 ring-1 ring-white/10">Reach: {r.potential_reach}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Platforms List */}
        <div className="mt-8 rounded-2xl bg-zinc-900/80 p-5 ring-1 ring-white/10 shadow-xl">
          <Section
            title="Platform Analysis (All Platforms)"
            icon={Globe}
            right={
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400"/>
                  <input
                    className="pl-9 pr-3 py-2 rounded-xl bg-zinc-950/70 ring-1 ring-white/10 text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-sky-500"
                    placeholder="Search platforms..."
                    value={query}
                    onChange={e=>setQuery(e.target.value)}
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-zinc-400"/>
                  <select value={filter} onChange={e=>setFilter(e.target.value)} className="bg-zinc-950/70 ring-1 ring-white/10 rounded-xl px-3 py-2 text-sm">
                    <option value="all">All</option>
                    <option value="found">Found</option>
                    <option value="missing">Missing</option>
                  </select>
                  <select value={sort} onChange={e=>setSort(e.target.value)} className="bg-zinc-950/70 ring-1 ring-white/10 rounded-xl px-3 py-2 text-sm">
                    <option value="default">Sort</option>
                    <option value="followers">Followers</option>
                    <option value="completeness">Completeness</option>
                    <option value="name">Name (A-Z)</option>
                  </select>
                </div>
              </div>
            }
          />

          <div className="mt-4 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((p) => (
              <PlatformCard key={p.name} p={p} />
            ))}
          </div>
        </div>

        {/* Meta */}
        <div className="mt-8 rounded-2xl bg-zinc-900/80 p-5 ring-1 ring-white/10 shadow-xl">
          <Section title="Analyzer Meta" icon={Globe} />
          <div className="mt-3 grid md:grid-cols-3 gap-3 text-sm">
            <div className="p-4 rounded-2xl bg-zinc-950/70 ring-1 ring-white/10">
              <p className="text-zinc-400 text-xs">Analyzer Version</p>
              <p className="text-white font-medium mt-1">{RAW.meta.analyzer_version}</p>
            </div>
            <div className="p-4 rounded-2xl bg-zinc-950/70 ring-1 ring-white/10">
              <p className="text-zinc-400 text-xs">Platforms Supported</p>
              <p className="text-white font-medium mt-1">{RAW.meta.platforms_supported}</p>
            </div>
            <div className="p-4 rounded-2xl bg-zinc-950/70 ring-1 ring-white/10">
              <p className="text-zinc-400 text-xs">Method</p>
              <p className="text-white font-medium mt-1">{RAW.meta.analysis_method}</p>
            </div>
          </div>
        </div>

        <footer className="mt-10 pb-6 text-center text-xs text-zinc-500">
          Built with ❤ for {brand.brand_name}. Dark cards for emphasis as requested.
        </footer>
      </div>
    </div>
  );
}
