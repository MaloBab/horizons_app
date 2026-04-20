import { ref, computed, reactive } from 'vue'
import type { PasswordStrength } from '../types/auth.types'

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string
}

type FormErrors<T> = Partial<Record<keyof T, string>>

export function useFormValidation() {
  const loginForm = reactive<LoginForm>({ username: '', password: '' })
  const registerForm = reactive<RegisterForm>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  const loginErrors = ref<FormErrors<LoginForm>>({})
  const registerErrors = ref<FormErrors<RegisterForm>>({})

  const passwordStrength = computed<PasswordStrength>(() => {
    const pwd = registerForm.password
    if (!pwd) return { score: 0, label: '', color: '' }

    let score = 0
    if (pwd.length >= 8) score++
    if (/[A-Z]/.test(pwd)) score++
    if (/[0-9]/.test(pwd)) score++
    if (/[^A-Za-z0-9]/.test(pwd)) score++

    const levels: PasswordStrength[] = [
      { score: 0, label: '', color: '' },
      { score: 1, label: 'Faible', color: '#ef4444' },
      { score: 2, label: 'Moyen', color: '#f59e0b' },
      { score: 3, label: 'Bon', color: '#3b82f6' },
      { score: 4, label: 'Fort', color: '#10b981' },
    ]
    return levels[score] || { score: 0, label: '', color: '' }
  })

  function validateLogin(): boolean {
    const errors: FormErrors<LoginForm> = {}
    if (!loginForm.username.trim()) errors.username = "Nom d'utilisateur requis"
    if (!loginForm.password) errors.password = 'Mot de passe requis'
    loginErrors.value = errors
    return Object.keys(errors).length === 0
  }

  function validateRegister(): boolean {
    const errors: FormErrors<RegisterForm> = {}
    const emailRx = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    if (registerForm.username.trim().length < 3)
      errors.username = "Nom d'utilisateur trop court (min. 3 caractères)"
    if (!emailRx.test(registerForm.email))
      errors.email = 'Adresse email invalide'
    if (registerForm.password.length < 8)
      errors.password = 'Mot de passe trop court (min. 8 caractères)'
    if (registerForm.password !== registerForm.confirmPassword)
      errors.confirmPassword = 'Les mots de passe ne correspondent pas'

    registerErrors.value = errors
    return Object.keys(errors).length === 0
  }

  function clearErrors() {
    loginErrors.value = {}
    registerErrors.value = {}
  }

  return {
    loginForm,
    registerForm,
    loginErrors,
    registerErrors,
    passwordStrength,
    validateLogin,
    validateRegister,
    clearErrors,
  }
}