from polymorphic.formsets import polymorphic_modelformset_factory, PolymorphicFormSetChild
from .models import SignPanel, TextPanel, ImagePanel

SignPanelFormSet = polymorphic_modelformset_factory(SignPanel, formset_children=(
    PolymorphicFormSetChild(TextPanel),
    PolymorphicFormSetChild(ImagePanel),
), exclude=[])