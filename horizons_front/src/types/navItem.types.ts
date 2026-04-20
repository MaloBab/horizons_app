import type { Component } from "vue"

export interface NavItem {
  label: string
  route: string
  icon?: Component
}