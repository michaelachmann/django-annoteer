from django.shortcuts import render, get_object_or_404, redirect
from projects.models import Project, Label

from .models import Annotation, AnnotationLabel
from django.contrib.auth.decorators import login_required
from .forms import AnnotationForm
from django.db.models import Count, Q
from dataitem.models import Dataitem


def next_dataitem(project, user):
    """
    Liefert das nächste Dataitem:
    – das noch < project.num_annotators Annotationen hat
    – das der gegebene User noch nicht annotiert hat
    oder None, wenn alles erledigt ist.
    """
    return (
        Dataitem.objects
        .filter(project=project)
        .annotate(
            total=Count('annotations', distinct=True),
            mine=Count('annotations', filter=Q(annotations__annotated_by=user), distinct=True)
        )
        .filter(total__lt=project.num_annotators, mine=0)
        .order_by('total', 'pk')
        .first()
    )

def annotation_list(request):
    annotation = Annotation.objects.all()
    return render(request, "annotation/annotation_list.html", {"annotation": annotation})

def annotation_detail(request, pk):
    annotation = get_object_or_404(Annotation, pk=pk)
    return render(request, "annotation/annotation_detail.html", {"annotation": annotation})

@login_required
def annotation_create(request):
    if request.method == "POST":
        form = AnnotationForm(request.POST)
        if form.is_valid():
            annotation = form.save(commit=False)
            annotation.created_by = request.user
            annotation.save()
            return redirect("annotation:annotation_list")
    else:
        form = AnnotationForm()
    return render(request, "annotation/annotation_form.html", {"form": form})

@login_required
def annotation_update(request, pk):
    annotation = get_object_or_404(Annotation, pk=pk)
    form = AnnotationForm(request.POST or None, instance=annotation)
    if form.is_valid():
        form.save()
        return redirect("annotation:annotation_list")
    return render(request, "annotation/annotation_form.html", {"form": form})

@login_required
def annotation_delete(request, pk):
    annotation = get_object_or_404(Annotation, pk=pk)
    if request.method == "POST":
        annotation.delete()
        return redirect("annotation:annotation_list")
    return render(request, "annotation/annotation_confirm_delete.html", {"annotation": annotation})


@login_required
def annotate_view(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    dataitem = next_dataitem(project, request.user)

    if not dataitem:
        return render(request, "annotation/annotation_all_done.html", {"project": project})

    existing_annotation = Annotation.objects.filter(dataitem=dataitem, annotated_by=request.user).first()
    if existing_annotation:
        return redirect("annotation:annotate", pk=project.pk)

    if request.method == "POST":
        if project.label_type == "SI":
            label_id = request.POST.get("label")
            if label_id:
                label = get_object_or_404(Label, pk=label_id)
                annotation = Annotation.objects.create(
                    dataitem=dataitem,
                    annotated_by=request.user,
                    last_modified_by=request.user,
                )
                AnnotationLabel.objects.create(
                    annotation=annotation,
                    label=label,
                )
                return redirect("annotation:annotate", pk=project.pk)
            else:
                form = AnnotationForm(request.POST)

        elif project.label_type == "MU":
            label_ids = request.POST.getlist("labels")
            if label_ids:
                annotation = Annotation.objects.create(
                    dataitem=dataitem,
                    annotated_by=request.user,
                    last_modified_by=request.user,
                )
                for label_id in label_ids:
                    label = get_object_or_404(Label, pk=label_id)
                    AnnotationLabel.objects.create(
                        annotation=annotation,
                        label=label,
                    )
            return redirect("annotation:annotate", pk=project.pk)
        else:
            form = AnnotationForm(request.POST)

    else:
        form = AnnotationForm()

    return render(request, "annotation/annotate.html", {
        "form": form,
        "dataitem": dataitem,
        "project": project
    })