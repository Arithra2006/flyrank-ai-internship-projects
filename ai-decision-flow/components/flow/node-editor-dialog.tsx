"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Trash2 } from "lucide-react";

interface NodeEditorDialogProps {
  open: boolean;
  initialLabel: string;
  initialPrompt: string;
  isStartNode: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (label: string, prompt: string) => void;
  onDelete: () => void;
  onSetStart: () => void;
}

export function NodeEditorDialog({
  open,
  initialLabel,
  initialPrompt,
  isStartNode,
  onOpenChange,
  onSave,
  onDelete,
  onSetStart,
}: NodeEditorDialogProps) {
  const [label, setLabel] = useState(initialLabel);
  const [prompt, setPrompt] = useState(initialPrompt);

  useEffect(() => {
    setLabel(initialLabel);
    setPrompt(initialPrompt);
  }, [initialLabel, initialPrompt, open]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Decision Node</DialogTitle>
          <DialogDescription>
            The AI will evaluate this prompt and respond with YES or NO to
            decide which path the workflow takes next.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4">
          <div className="grid gap-1.5">
            <Label htmlFor="node-label">Node title</Label>
            <Input
              id="node-label"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="e.g. Support Request Check"
            />
          </div>

          <div className="grid gap-1.5">
            <Label htmlFor="node-prompt">Decision prompt</Label>
            <Textarea
              id="node-prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder='e.g. "Is this message related to technical support?"'
              rows={4}
            />
          </div>

          <div className="flex items-center justify-between rounded-md border border-dashed border-slate-300 px-3 py-2">
            <span className="text-xs text-slate-500">
              {isStartNode
                ? "This is the workflow's start node."
                : "Mark this as the workflow's start node."}
            </span>
            <Button
              size="sm"
              variant={isStartNode ? "secondary" : "outline"}
              disabled={isStartNode}
              onClick={onSetStart}
            >
              {isStartNode ? "Start node" : "Set as start"}
            </Button>
          </div>
        </div>

        <DialogFooter className="mt-2">
          <Button
            variant="destructive"
            size="sm"
            className="sm:mr-auto"
            onClick={onDelete}
          >
            <Trash2 className="h-3.5 w-3.5" />
            Delete node
          </Button>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              onSave(label.trim() || "Untitled Node", prompt.trim());
              onOpenChange(false);
            }}
          >
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
