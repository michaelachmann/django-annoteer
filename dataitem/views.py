from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataitem
from .forms import DataitemForm
from .forms import DataImportForm
from .models import Dataitem
from projects.models import Project

def dataitem_list(request):
    dataitems = Dataitem.objects.all()
    return render(request, "dataitem/dataitem_list.html", {"dataitem": dataitem})


def dataitem_detail(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    return render(request, "dataitem/dataitem_detail.html", {"dataitem": dataitem})


@login_required
def dataitem_create(request):
    if request.method == "POST":
        form = DataitemForm(request.POST)
        if form.is_valid():
            dataitem = form.save(commit=False)
            dataitem.created_by = request.user
            # Optionally set project here if applicable
            dataitem.save()
            return redirect("dataitem:dataitem_list")
    else:
        form = DataitemForm()
    return render(request, "dataitem/dataitem_form.html", {"form": form})


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
                return redirect("data_import", project_pk=project.pk)

            created_count = 0
            skipped_count = 0

            for row in reader:
                ext_id = row["id"].strip()
                text = row["text"].strip()

                if not ext_id or not text:
                    skipped_count += 1
                    continue

                obj, created = Dataitem.objects.get_or_create(
                    external_id=ext_id,
                    defaults={
                        "text": text,
                        "project": project,
                        "name": f"Imported {ext_id}",
                        "description": "",
                        "created_by": request.user
                    }
                )

                if created:
                    created_count += 1
                else:
                    # You could choose to update text here
                    # obj.text = text
                    # obj.save()
                    skipped_count += 1

            messages.success(
                request,
                f"Import complete: {created_count} new items, {skipped_count} skipped."
            )
            return redirect("project_detail", pk=project.pk)
    else:
        form = DataImportForm()

    return render(request, "dataitem/data_import.html", {
        "project": project,
        "form": form
    })