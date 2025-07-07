from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataitem
from .forms import DataitemForm
from .forms import DataImportForm
from .models import Dataitem, DataBatch
from projects.models import Project
import csv
from io import TextIOWrapper
from django.contrib import messages
from django.http import HttpResponseBadRequest

def dataitem_list(request):
    dataitem = Dataitem.objects.all()
    return render(request, "dataitem/dataitem_list.html", {"dataitem": dataitem})


def dataitem_detail(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    return render(request, "dataitem/dataitem_detail.html", {"dataitem": dataitem})


@login_required
def dataitem_create(request):
    project_id = request.GET.get("project")

    if not project_id:
        return HttpResponseBadRequest("A project ID is required to create a Dataitem.")

    if request.method == "POST":
        form = DataitemForm(request.POST)
        if form.is_valid():
            dataitem = form.save(commit=False)
            dataitem.created_by = request.user
            dataitem.project_id = project_id
            dataitem.save()
            return redirect("projects:project_detail", pk=project_id)
    else:
        form = DataitemForm()

    return render(request, "dataitems/dataitem_form.html", {"form": form})




@login_required
def dataitem_update(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    form = DataitemForm(request.POST or None, instance=dataitem)
    if form.is_valid():
        form.save()
        return redirect("dataitem:dataitem_detail", pk=dataitem.pk)
    return render(request, "dataitem/dataitem_form.html", {"form": form})


@login_required
def dataitem_delete(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    if request.method == "POST":
        dataitem.delete()
        return redirect("dataitem:dataitem_list")
    return render(request, "dataitem/dataitem_confirm_delete.html", {"dataitem": dataitem})

@login_required
def data_import_view(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)

    if request.method == "POST":
        form = DataImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]
            decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8")
            reader = csv.DictReader(decoded_file)

            required_fields = {"id", "text"}
            if not required_fields.issubset(reader.fieldnames):
                messages.error(request, "CSV must contain 'id' and 'text' columns.")
                return redirect("dataitems:data_import", project_pk=project.pk)

            # ✅ Create DataBatch
            batch = DataBatch.objects.create(
                project=project,
                name=csv_file.name,
                uploaded_by=request.user
            )

            items = []
            for row in reader:
                ext_id = (row.get("id") or "").strip()
                text = (row.get("text") or "").strip()

                # Skip empty rows
                if not ext_id or not text:
                    continue

                item = Dataitem(
                    project=project,
                    batch=batch,
                    external_id=ext_id,
                    text=text,
                    created_by=request.user,
                    name=f"Imported {ext_id}",
                    description=""
                )
                items.append(item)

            total_items = len(items)

            if total_items == 0:
                messages.warning(request, "Keine gültigen Zeilen zum Import gefunden.")
                return redirect("dataitems:data_import", project_pk=project.pk)

            # ✅ Bulk create with ignore_conflicts (duplicates skipped automatically)
            Dataitem.objects.bulk_create(items, ignore_conflicts=True)

            # ✅ Count how many were actually created in this batch
            created_count = Dataitem.objects.filter(batch=batch).count()
            skipped_count = total_items - created_count

            messages.success(
                request,
                f"{created_count} neue Texte importiert, {skipped_count} Duplikate übersprungen."
            )
            return redirect("projects:project_detail", pk=project.pk)

    else:
        form = DataImportForm()

    return render(request, "dataitems/data_import.html", {
        "project": project,
        "form": form
    })

@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(DataBatch, pk=pk)
    items = batch.dataitems.all()
    return render(request, "dataitems/batch_detail.html", {"batch": batch, "dataitems": items})

print("=== Running import_csv ===")