export const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "Pricing", href: "/pricing" },
] as const;

export const RESOURCES_LINKS = [
  { label: "Documentation", href: "/docs" },
  { label: "Updates & Changelog", href: "/updates" },
  { label: "Support", href: "/support" },
] as const;

export const STATS = [
  { value: 424, label: "Problems Analyzed" },
  { value: 708, label: "Submissions Processed" },
  { value: 47, label: "Topics Covered" },
  { value: 12, label: "Weakness Patterns" },
] as const;

export const RADAR_AXES = [
  "Arrays",
  "Trees",
  "DP",
  "Graphs",
  "Two Pointers",
  "Backtracking",
] as const;

export const RADAR_VALUES = [0.89, 0.55, 0.23, 0.42, 0.71, 0.38];
export const RADAR_IDEAL = [0.95, 0.9, 0.85, 0.88, 0.92, 0.87];

export interface LearningNode {
  label: string;
  completed: boolean;
  current?: boolean;
}

export const LEARNING_PATH_NODES: LearningNode[] = [
  { label: "Arrays", completed: true },
  { label: "Hash Map", completed: true },
  { label: "Two Pointers", completed: true },
  { label: "Sliding Window", completed: false, current: true },
  { label: "Linked List", completed: false },
  { label: "Trees", completed: false },
  { label: "DFS", completed: false },
];

export const SOCIAL_LINKS = [
  { label: "GitHub", href: "https://github.com" },
  { label: "Twitter", href: "https://twitter.com" },
  { label: "Discord", href: "https://discord.com" },
] as const;
