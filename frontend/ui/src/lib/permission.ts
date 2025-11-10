// src/lib/permissions.ts
import type { Role } from "./session";

// --- Actions available in the system ---
export const ACTIONS = [
  "view",
  "create",
  "edit",
  "delete",
  "approve",
  "export",
] as const;

export type Action = typeof ACTIONS[number];

// Simple dependency: if any of these are enabled, "view" must be enabled
export const ACTION_DEPENDENCIES: Record<Action, Action[]> = {
  view: [],
  create: ["view"],
  edit: ["view"],
  delete: ["view"],
  approve: ["view"],
  export: ["view"],
};

// --- Features (resources) to secure ---
export type FeatureKey =
  | "users"
  | "roles"
  | "permissions"
  | "products"
  | "orders"
  | "invoices"
  | "reports";

export type Feature = {
  key: FeatureKey;
  label: string;
  description?: string;
};

export const FEATURES: Feature[] = [
  { key: "users", label: "Users", description: "Manage user accounts" },
  { key: "roles", label: "Roles", description: "Role definitions" },
  { key: "permissions", label: "Permissions", description: "Access policies" },
  { key: "products", label: "Products", description: "Catalog items" },
  { key: "orders", label: "Orders", description: "Sales orders" },
  { key: "invoices", label: "Invoices", description: "Billing docs" },
  { key: "reports", label: "Reports", description: "Operational reports" },
];

// --- A single role's permissions: feature -> action -> boolean ---
export type RolePolicy = Record<FeatureKey, Record<Action, boolean>>;

// Utility to build an empty policy
export function emptyPolicy(): RolePolicy {
  const base: any = {};
  for (const f of FEATURES) {
    base[f.key] = {} as Record<Action, boolean>;
    for (const a of ACTIONS) base[f.key][a] = false;
  }
  return base;
}

// Merge dependencies for a (feature, action) toggle
export function withDependencies(
  policy: RolePolicy,
  feature: FeatureKey,
  action: Action,
  value: boolean
): RolePolicy {
  const next: RolePolicy = JSON.parse(JSON.stringify(policy));
  next[feature][action] = value;

  // if enabling, also enable what it depends on
  if (value) {
    for (const dep of ACTION_DEPENDENCIES[action]) {
      next[feature][dep] = true;
    }
  } else {
    // if disabling "view", disable all that depend on it
    if (action === "view") {
      for (const a of ACTIONS) {
        if (a !== "view" && ACTION_DEPENDENCIES[a].includes("view")) {
          next[feature][a] = false;
        }
      }
    }
  }
  return next;
}

// --- Sensible defaults per role (you can tweak anytime) ---
export const DEFAULT_POLICIES: Record<Role, RolePolicy> = {
  admin: (() => {
    const p = emptyPolicy();
    for (const f of FEATURES) for (const a of ACTIONS) p[f.key][a] = true;
    return p;
  })(),
  creator: (() => {
    const p = emptyPolicy();
    for (const f of FEATURES) {
      p[f.key].view = true;
      p[f.key].create = true;
      p[f.key].edit = true;
      p[f.key].export = f.key === "reports"; // can export reports
    }
    // Limit administrative areas
    p.users.delete = false;
    p.roles.delete = false;
    p.permissions.delete = false;
    p.roles.approve = false;
    p.permissions.approve = false;
    return p;
  })(),
  reviewer: (() => {
    const p = emptyPolicy();
    for (const f of FEATURES) {
      p[f.key].view = true;
      p[f.key].approve = f.key !== "permissions" && f.key !== "roles";
      p[f.key].export = f.key === "reports";
    }
    return p;
  })(),
  viewer: (() => {
    const p = emptyPolicy();
    for (const f of FEATURES) {
      p[f.key].view = true;
      p[f.key].export = f.key === "reports";
    }
    return p;
  })(),
};
