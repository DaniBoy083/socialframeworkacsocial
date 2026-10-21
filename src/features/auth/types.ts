export interface Actor {
  id: string;
  name: string;
  email: string;
  teams: string[];
  permissions: string[];
  isTechnology: boolean;
}
export interface Session {
  authenticated: true;
  actor: Actor;
}
