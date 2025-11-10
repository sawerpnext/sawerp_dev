export type Role = "admin" | "creator" | "reviewer" | "viewer";

export const ROLES: Role[] = ["admin", "creator", "reviewer", "viewer"];

// ...rest of your session code...

let currentRole: Role | null = null;

export function setRole(role: Role) {
    currentRole = role;
    // Optional: persist in localStorage
    localStorage.setItem("userRole", role);
}

export function getRole(): Role | null {
    if (!currentRole) {
        // Try to restore from localStorage
        const stored = localStorage.getItem("userRole") as Role | null;
        if (stored && isValidRole(stored)) {
            currentRole = stored;
        }
    }
    return currentRole;
}

export function clearRole() {
    currentRole = null;
    localStorage.removeItem("userRole");
}

function isValidRole(role: string): role is Role {
    return ["admin", "creator", "reviewer", "viewer"].includes(role);
}