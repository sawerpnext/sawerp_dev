import { Navigate, Outlet } from "react-router-dom";
import { getRole, type Role } from "../lib/session";

interface Props {
    allow: Role[];
}

const PrivateRoute: React.FC<Props> = ({ allow }) => {
    const role = getRole();
    
    if (!role) {
        // Not logged in
        return <Navigate to="/login" replace />;
    }
    
    if (!allow.includes(role)) {
        // Wrong role
        return <Navigate to={`/${role}`} replace />;
    }
    
    // Authorized
    return <Outlet />;
};

export default PrivateRoute;