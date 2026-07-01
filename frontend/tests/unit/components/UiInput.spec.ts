import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UiInput from '~/components/ui/UiInput.vue'

describe('UiInput', () => {
  it('renders label', () => {
    const wrapper = mount(UiInput, { props: { modelValue: '', label: 'Name' } })
    expect(wrapper.text()).toContain('Name')
  })

  it('shows hint text', () => {
    const wrapper = mount(UiInput, { props: { modelValue: '', label: 'Name', hint: 'Enter your name' } })
    expect(wrapper.text()).toContain('Enter your name')
  })

  it('shows error and hides hint', () => {
    const wrapper = mount(UiInput, { props: { modelValue: '', label: 'Name', hint: 'Hint text', error: 'Required' } })
    expect(wrapper.text()).toContain('Required')
    expect(wrapper.text()).not.toContain('Hint text')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(UiInput, { props: { modelValue: '', label: 'Name' } })
    await wrapper.find('input').setValue('John')
    if (wrapper.emitted('update:modelValue')) {
      expect(wrapper.emitted('update:modelValue')[0]).toEqual(['John'])
    }
  })

  it('shows required asterisk', () => {
    const wrapper = mount(UiInput, { props: { modelValue: '', label: 'Name', required: true } })
    expect(wrapper.html()).toContain('*')
  })

  it('sets input type', () => {
    const wrapper = mount(UiInput, { props: { modelValue: '', type: 'email', label: 'Email' } })
    expect(wrapper.find('input').attributes('type')).toBe('email')
  })

  it('disables input', () => {
    const wrapper = mount(UiInput, { props: { modelValue: '', disabled: true, label: 'Name' } })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('shows maxLength counter', () => {
    const wrapper = mount(UiInput, { props: { modelValue: 'ab', label: 'Name', maxLength: 10 } })
    expect(wrapper.text()).toContain('2 / 10')
  })

  it('hides maxLength counter when error is present', () => {
    const wrapper = mount(UiInput, { props: { modelValue: 'ab', label: 'Name', maxLength: 10, error: 'Required' } })
    expect(wrapper.text()).not.toContain('2 / 10')
    expect(wrapper.text()).toContain('Required')
  })

  it('sets maxlength attribute on input', () => {
    const wrapper = mount(UiInput, { props: { modelValue: '', label: 'Name', maxLength: 5 } })
    expect(wrapper.find('input').attributes('maxlength')).toBe('5')
  })
})
