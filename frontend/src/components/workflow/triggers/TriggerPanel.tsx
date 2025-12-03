"use client";

import { CalendarClock, Link2, Loader2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useScheduleTriggers, useWebhookTriggers } from "@/hooks/useTriggers";

import { ScheduleTriggerForm } from "./ScheduleTriggerForm";
import { ScheduleTriggerList } from "./ScheduleTriggerList";
import { WebhookTriggerForm } from "./WebhookTriggerForm";
import { WebhookTriggerList } from "./WebhookTriggerList";

interface TriggerPanelProps {
  workflowId: string;
}

export function TriggerPanel({ workflowId }: TriggerPanelProps) {
  const [activeTab, setActiveTab] = useState<"schedule" | "webhook">(
    "schedule"
  );
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [showWebhookForm, setShowWebhookForm] = useState(false);

  const {
    triggers: scheduleTriggers,
    isLoading: isScheduleLoading,
    createTrigger: createScheduleTrigger,
    deleteTrigger: deleteScheduleTrigger,
    toggleTrigger: toggleScheduleTrigger,
  } = useScheduleTriggers(workflowId);

  const {
    triggers: webhookTriggers,
    isLoading: isWebhookLoading,
    createTrigger: createWebhookTrigger,
    deleteTrigger: deleteWebhookTrigger,
    regenerateSecret,
  } = useWebhookTriggers(workflowId);

  const handleScheduleCreate = async (cronExpression: string) => {
    await createScheduleTrigger({ cron_expression: cronExpression });
    setShowScheduleForm(false);
  };

  const handleWebhookCreate = async (webhookPath: string) => {
    const trigger = await createWebhookTrigger({ webhook_path: webhookPath });
    setShowWebhookForm(false);
    return trigger;
  };

  const isLoading = isScheduleLoading || isWebhookLoading;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CalendarClock className="h-5 w-5" />
          トリガー設定
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs
          value={activeTab}
          onValueChange={(v) => setActiveTab(v as "schedule" | "webhook")}
        >
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="schedule" className="flex items-center gap-2">
              <CalendarClock className="h-4 w-4" />
              スケジュール
              {scheduleTriggers.length > 0 && (
                <span className="bg-primary/10 text-primary ml-1 rounded-full px-2 py-0.5 text-xs">
                  {scheduleTriggers.length}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="webhook" className="flex items-center gap-2">
              <Link2 className="h-4 w-4" />
              Webhook
              {webhookTriggers.length > 0 && (
                <span className="bg-primary/10 text-primary ml-1 rounded-full px-2 py-0.5 text-xs">
                  {webhookTriggers.length}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="schedule" className="mt-4 space-y-4">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : (
              <>
                {showScheduleForm ? (
                  <ScheduleTriggerForm
                    onSubmit={handleScheduleCreate}
                    onCancel={() => setShowScheduleForm(false)}
                  />
                ) : (
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => setShowScheduleForm(true)}
                  >
                    + スケジュールトリガーを追加
                  </Button>
                )}

                <ScheduleTriggerList
                  triggers={scheduleTriggers}
                  onDelete={deleteScheduleTrigger}
                  onToggle={toggleScheduleTrigger}
                />
              </>
            )}
          </TabsContent>

          <TabsContent value="webhook" className="mt-4 space-y-4">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : (
              <>
                {showWebhookForm ? (
                  <WebhookTriggerForm
                    onSubmit={handleWebhookCreate}
                    onCancel={() => setShowWebhookForm(false)}
                  />
                ) : (
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => setShowWebhookForm(true)}
                  >
                    + Webhookトリガーを追加
                  </Button>
                )}

                <WebhookTriggerList
                  triggers={webhookTriggers}
                  onDelete={deleteWebhookTrigger}
                  onRegenerateSecret={regenerateSecret}
                />
              </>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
