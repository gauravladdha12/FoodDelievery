from django.shortcuts import render

# Create your views here.

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from foody import settings
import heapq


class DeliveryTimeViewSet(viewsets.ViewSet):
    slots_in_kitchen = settings.SLOTS_IN_KITCHEN
    appetizer_slot = settings.APPETIZER_SLOT_REQUIRED
    main_course_slot = settings.MAIN_COURSE_SLOT_REQUIRED
    delivery_time_in_minutes = settings.DELIVERY_TIME_PER_KM_IN_MINUTES
    appetizer_time_required = settings.APPETIZER_TIME_REQUIRED_IN_MINUTES
    main_course_time_required = settings.MAIN_COURSE_TIME_REQUIRED_IN_MINUTES
    restaurant_deny_time = settings.RESTAURANT_DENY_TIME_IN_MINUTES

    def validate_order(self, order, order_ids):
        if "orderId" in order:
            order_id = order["orderId"]
            if not str(order_id).isdigit() or len(str(order_id)) != 2:
                message = ("Order {} is denied, because the order Id is not in right format.".format(
                    order['orderId']))
                return False, message

            if order_id in order_ids:
                message = ("Order {} is denied, because Duplicate order Id countere.".format(
                    order['orderId']))
                return False, message

        else:
            message = ("Order {} is denied, because No order id is present.".format(
                order['orderId']))
            return False, message

        if not "meals" in order:
            message = ("Order {} is denied, because No meals are present.".format(
                order['orderId']))
            return False, message

        if not "distance" in order:
            message = ("Order {} is denied, because No distance is present.".format(
                order['orderId']))
            return False, message

        return True, None

    def get_time_for_slots(self, kitchen_slot_free_time, slots_required):
        max_time = 0
        slots_free_time_list = []
        for slot in range(slots_required):
            free_time = heapq.heappop(kitchen_slot_free_time)
            max_time = max(max_time, free_time)
            slots_free_time_list.append(free_time)

        return max_time, slots_free_time_list

    def add_slots_free_time_list(self, kitchen_slot_free_time, slots_free_time_list):
        for time in slots_free_time_list:
            heapq.heappush(kitchen_slot_free_time, time)

    def fill_final_time(self, kitchen_slot_free_time, slots_required, time_for_order):
        for time in range(slots_required):
            heapq.heappush(kitchen_slot_free_time, time_for_order)

    def get_time_for_meal(self, meals, order_id, delivery_distance, kitchen_slot_free_time,):
        slots_required = 0
        for meal in meals:
            if meal == 'A':
                slots_required += self.appetizer_slot

            elif meal == 'M':
                slots_required += self.main_course_slot

            else:
                message = (
                    "Order {} is denied, because the restaurant cannot accommodate it.".format(order_id))
                return None, message

        if slots_required > self.slots_in_kitchen:
            message = (
                "Order {} is denied, because the restaurant cannot deliver it on time.".format(order_id))
            return None, message
        # getting waiting time from heap
        inital_time_required, slots_free_time_list = self.get_time_for_slots(
            kitchen_slot_free_time, slots_required)

        if 'M' in meals:
            prep_time = self.main_course_time_required
        else:
            prep_time = self.appetizer_time_required

        delivery_time = delivery_distance*self.delivery_time_in_minutes
        time_for_order = inital_time_required + prep_time + delivery_time

        if time_for_order > self.restaurant_deny_time:
            # deny order
            message = (
                "Order {} is denied, because the restaurant cannot deliver it on time.".format(order_id))
            # adding back initial time
            self.add_slots_free_time_list(
                kitchen_slot_free_time, slots_free_time_list)
            return None, message

        # adding final time to each slot
        self.fill_final_time(kitchen_slot_free_time,
                             slots_required, time_for_order)
        return time_for_order, None

    def process_delivery_time(self, order_data):
        json_response = []
        # creating slots of kitchen
        kitchen_slot_free_time = [0]*self.slots_in_kitchen
        # min heap for storing time of free of each slot
        heapq.heapify(kitchen_slot_free_time)
        order_ids = []
        for order in order_data:
            order_id = order['orderId']
            distance = order['distance']
            # validating input
            status, message = self.validate_order(order, order_ids)
            if not status:
                response = {}
                response['message'] = message
                json_response.append(response)
                continue
            order_ids.append(order_id)
            meals = order['meals']
            # getting final time of order
            time_for_order, message = self.get_time_for_meal(
                meals, order_id, distance, kitchen_slot_free_time)
            if time_for_order:
                response = {}
                response['message'] = ("Order {} will get delivered in {} minutes".format(
                    order["orderId"], time_for_order))
            else:
                response = {}
                response['message'] = message

            json_response.append(response)
        return json_response

    @action(methods=["post"], detail=False, url_path="get-delivery-time", url_name="geet-delivery-time")
    def get_delivery_time(self, request, *args, **kwargs):
        try:
            order_data = request.data
            # checking base condition
            if len(order_data) == 0:
                response = {
                    'message': 'No order is placed'
                }
                return Response(response, status=200)

            result = self.process_delivery_time(order_data)
            return Response(result, status=200)
        except Exception as e:
            response = {}
            response['message'] = str(e)
            return Response(response, 400)
