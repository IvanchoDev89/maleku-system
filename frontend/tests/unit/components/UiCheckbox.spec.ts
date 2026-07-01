import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import UiCheckbox from '~/components/ui/UiCheckbox.vue'

describe('UiCheckbox', () => {
  it('renders label', () => {
    const wrapper = mount(UiCheckbox, { props: { modelValue: false, label: 'Accept terms' } })
    expect(wrapper.text()).toContain('Accept terms')
  })

  it('emits update:modelValue with true when checked', async () => {
    const wrapper = mount(UiCheckbox, { props: { modelValue: false, label: 'Test' } })
    await wrapper.find('input').setValue(true)
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    if (wrapper.emitted('update:modelValue')) {
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([true])
    }
  })

  it('does not emit when disabled', async () => {
    const wrapper = mount(UiCheckbox, { props: { modelValue: false, disabled: true, label: 'Test' } })
    await wrapper.find('input').setValue(true)
    expect(wrapper.emitted('update:modelValue')).toBeFalsy()
  })

  it('applies indeterminate prop without crashing', () => {
    const wrapper = mount(UiCheckbox, { props: { modelValue: false, indeterminate: true, label: 'Test' } })
    expect(wrapper.find('input').attributes('type')).toBe('checkbox')
    expect(wrapper.find('input').attributes('checked')).toBeUndefined()
  })

  it('reacts to indeterminate prop change', async () => {
    const wrapper = mount(UiCheckbox, { props: { modelValue: false, indeterminate: false, label: 'Test' } })
    await wrapper.setProps({ indeterminate: true })
    expect(wrapper.find('input').attributes('type')).toBe('checkbox')
  })

  it('shows error message', () => {
    const wrapper = mount(UiCheckbox, { props: { modelValue: false, label: 'Test', error: 'Required' } })
    expect(wrapper.text()).toContain('Required')
  })

  it('shows required asterisk', () => {
    const wrapper = mount(UiCheckbox, { props: { modelValue: false, label: 'Test', required: true } })
    expect(wrapper.html()).toContain('*')
  })

  it('renders description', () => {
    const wrapper = mount(UiCheckbox, { props: { modelValue: false, label: 'Test', description: 'Some info' } })
    expect(wrapper.text()).toContain('Some info')
  })
})
