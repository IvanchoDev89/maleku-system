import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UiToggle from '~/components/ui/UiToggle.vue'

describe('UiToggle', () => {
  it('renders label', () => {
    const wrapper = mount(UiToggle, { props: { modelValue: false, label: 'Enable' } })
    expect(wrapper.text()).toContain('Enable')
  })

  it('emits update:modelValue with true on click when off', async () => {
    const wrapper = mount(UiToggle, { props: { modelValue: false, label: 'Test' } })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    if (wrapper.emitted('update:modelValue')) {
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([true])
    }
  })

  it('emits update:modelValue with false on click when on', async () => {
    const wrapper = mount(UiToggle, { props: { modelValue: true, label: 'Test' } })
    await wrapper.find('button').trigger('click')
    if (wrapper.emitted('update:modelValue')) {
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([false])
    }
  })

  it('toggles when clicking label', async () => {
    const wrapper = mount(UiToggle, { props: { modelValue: false, label: 'Clickable' } })
    await wrapper.find('label').trigger('click')
    if (wrapper.emitted('update:modelValue')) {
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([true])
    }
  })

  it('does not toggle when disabled', async () => {
    const wrapper = mount(UiToggle, { props: { modelValue: false, disabled: true, label: 'Test' } })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeFalsy()
  })

  it('applies small size classes', () => {
    const wrapper = mount(UiToggle, { props: { modelValue: false, size: 'sm', label: 'Test' } })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('w-8')
    expect(button.classes()).toContain('h-4')
  })

  it('applies default md size classes', () => {
    const wrapper = mount(UiToggle, { props: { modelValue: false, label: 'Test' } })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('w-11')
    expect(button.classes()).toContain('h-6')
  })

  it('renders description', () => {
    const wrapper = mount(UiToggle, { props: { modelValue: false, label: 'Test', description: 'Some info' } })
    expect(wrapper.text()).toContain('Some info')
  })
})
