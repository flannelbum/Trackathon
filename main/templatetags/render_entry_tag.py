from django import template

register = template.Library()

@register.inclusion_tag('main/individual_pledge.html')
def render_entry(entry):
    context_for_rendering_inclusion_tag = {'entry': entry}
    return context_for_rendering_inclusion_tag
