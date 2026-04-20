export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

export interface AuthNotification {
  message: string
  type: 'error' | 'success'
}

export type AuthMode = 'login' | 'register'

export interface PasswordStrength {
  score: 0 | 1 | 2 | 3 | 4
  label: string
  color: string
}