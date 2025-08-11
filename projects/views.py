from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from dataitem.models import Dataitem
from .models import Project, Label
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, LabelForm
from django.forms import inlineformset_factory
from annotation.models import Annotation, AnnotationLabel
from django.contrib.auth.models import User
from django.http import HttpResponse
import csv

# Projektliste

@login_required()
def project_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, "projects/project_list.html", {"projects": projects})

# Projektdetailseite
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    dataitems = Dataitem.objects.filter(project=project)
    return render(request, "projects/project_detail.html", {
        "project": project,
        "dataitems": dataitems,
    })

# Projekt erstellen
@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect("projects:project_list")
    else:
        form = ProjectForm()
    return render(request, "projects/project_form.html", {"form": form})

# Projekt aktualisieren
@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:project_list")
    else:
        error = form.errors
    return render(request, "projects/project_form.html", {"form": form, "error": error})

# Projekt löschen
@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    if request.method == "POST":
        project.delete()
        return redirect("projects:project_list")
    return render(request, "projects/project_confirm_delete.html", {"project": project})

# Labelverwaltung
@login_required
def label_manage(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.created_by != request.user:
        raise PermissionDenied

    LabelFormSet = inlineformset_factory(
        Project,
        Label,
        form=LabelForm,
        fields=("label", "value"),
        extra=1,
        can_delete=True
    )



    if request.method == "POST":
        formset = LabelFormSet(request.POST or None, instance=project)
        print("POST erhalten:", request.POST)
        print(formset.errors)
        if formset.is_valid():
            for form in formset:
                print("DELETE?", form.cleaned_data.get("DELETE"),
                      "| Label:", form.cleaned_data.get("label"),
                      "| Value:", form.cleaned_data.get("value"))
            formset.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        formset = LabelFormSet(instance=project)

    return render(request, "projects/label_manage.html", {
        "project": project,
        "formset": formset
    })

#Projekt exportieren
@login_required
def project_export(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.created_by != request.user:
        return HttpResponse("Access denied", status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="project_{project.pk}_annotations.csv"'

    writer = csv.writer(response)

    # all annotators
    annotators = User.objects.filter(annotations__dataitem__project=project).distinct()
    annotator_usernames = [user.username for user in annotators]

    # header
    header = ['external_id', 'text'] + annotator_usernames
    writer.writerow(header)

    dataitems = Dataitem.objects.filter(project=project)
    for item in dataitems:
        row = [item.external_id, item.text]

        for user in annotators:
            annotation = Annotation.objects.filter(dataitem= item, annotated_by=user).first()

            if annotation:
                labels = AnnotationLabel.objects.filter(annotation=annotation).values_list("label__label", flat=True)
                label_str = ";".join(labels) if project.label_type == "MU" else (labels[0] if labels else "")
            else:
                label_str = ""

            row.append(label_str)

        writer.writerow(row)

    return response
