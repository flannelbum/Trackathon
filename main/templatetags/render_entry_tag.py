from django import template

register = template.Library()

@register.inclusion_tag('main/individual_pledge.html')
def render_entry(entry):
    tags = ", ".join([(tag.name) for tag in entry.tags]) 
    context_for_rendering_inclusion_tag = {'entry': entry, 'tags': tags}
    return context_for_rendering_inclusion_tag
